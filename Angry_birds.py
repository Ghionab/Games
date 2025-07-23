import pygame
import sys
import math
import random

# Initialize pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Angry Birds Clone")

# Colors
SKY_BLUE = (135, 206, 235)
GROUND_GREEN = (34, 139, 34)
RED = (220, 60, 60)
YELLOW = (255, 215, 0)
BLUE = (30, 144, 255)
BROWN = (139, 69, 19)
GRAY = (169, 169, 169)
DARK_GRAY = (105, 105, 105)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
ORANGE = (255, 165, 0)
GREEN = (50, 205, 50)

# Physics constants
GRAVITY = 0.5
FRICTION = 0.99
ELASTICITY = 0.7

# Game variables
score = 0
birds = []
blocks = []
pigs = []
slingshot_pos = (150, HEIGHT - 200)
bird_radius = 20
bird_launched = False
trajectory_points = []
power = 0
angle = 0
max_power = 30
game_state = "aiming"  # aiming, flying, game_over
level = 1
birds_left = 3

class Bird:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.start_x = x
        self.start_y = y
        self.radius = bird_radius
        self.color = RED
        self.vx = 0
        self.vy = 0
        self.dragging = False
        self.launched = False
        self.destroyed = False
        
    def draw(self, surface):
        if not self.destroyed:
            # Draw bird body
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)
            # Draw eye
            pygame.draw.circle(surface, WHITE, (int(self.x + 5), int(self.y - 5)), 6)
            pygame.draw.circle(surface, BLACK, (int(self.x + 7), int(self.y - 5)), 3)
            # Draw beak
            beak_points = [
                (self.x + 10, self.y),
                (self.x + 25, self.y - 5),
                (self.x + 25, self.y + 5)
            ]
            pygame.draw.polygon(surface, ORANGE, beak_points)
    
    def update(self):
        if self.launched and not self.destroyed:
            # Apply gravity
            self.vy += GRAVITY
            
            # Apply friction
            self.vx *= FRICTION
            self.vy *= FRICTION
            
            # Update position
            self.x += self.vx
            self.y += self.vy
            
            # Boundary collision
            if self.x - self.radius < 0:
                self.x = self.radius
                self.vx = -self.vx * ELASTICITY
            elif self.x + self.radius > WIDTH:
                self.x = WIDTH - self.radius
                self.vx = -self.vx * ELASTICITY
                
            if self.y - self.radius < 0:
                self.y = self.radius
                self.vy = -self.vy * ELASTICITY
            elif self.y + self.radius > HEIGHT - 100:  # Ground level
                self.y = HEIGHT - 100 - self.radius
                self.vy = -self.vy * ELASTICITY
                self.vx *= 0.9  # Extra friction on ground
                
                # Stop if moving very slowly
                if abs(self.vx) < 0.5 and abs(self.vy) < 0.5:
                    self.vx = 0
                    self.vy = 0
                    
            # Check if bird is out of bounds or stopped
            if (self.x < -50 or self.x > WIDTH + 50 or 
                self.y > HEIGHT + 50 or 
                (abs(self.vx) < 0.1 and abs(self.vy) < 0.1 and self.y > HEIGHT - 150)):
                self.destroyed = True
                return True
                
        return False
    
    def launch(self, power, angle):
        self.launched = True
        self.vx = power * math.cos(angle)
        self.vy = power * math.sin(angle)
        
    def check_collision(self, obj):
        if self.destroyed:
            return False
            
        # Simple circle-rectangle collision
        dx = max(obj.x - self.x, 0, self.x - (obj.x + obj.width)) if self.x < obj.x or self.x > obj.x + obj.width else 0
        dy = max(obj.y - self.y, 0, self.y - (obj.y + obj.height)) if self.y < obj.y or self.y > obj.y + obj.height else 0
        
        return (dx * dx + dy * dy) < (self.radius * self.radius)

class Block:
    def __init__(self, x, y, width, height, material="wood"):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.material = material
        self.health = 100
        self.destroyed = False
        
        if material == "wood":
            self.color = BROWN
        elif material == "stone":
            self.color = GRAY
        elif material == "ice":
            self.color = BLUE
            
    def draw(self, surface):
        if not self.destroyed:
            pygame.draw.rect(surface, self.color, (self.x, self.y, self.width, self.height))
            pygame.draw.rect(surface, DARK_GRAY, (self.x, self.y, self.width, self.height), 2)
            
            # Draw cracks if damaged
            if self.health < 70:
                pygame.draw.line(surface, BLACK, (self.x, self.y + self.height//2), 
                                (self.x + self.width, self.y + self.height//2), 2)
            if self.health < 40:
                pygame.draw.line(surface, BLACK, (self.x + self.width//2, self.y), 
                                (self.x + self.width//2, self.y + self.height), 2)
    
    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.destroyed = True
            return True
        return False

class Pig:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 25
        self.health = 100
        self.destroyed = False
        
    def draw(self, surface):
        if not self.destroyed:
            # Draw pig body
            pygame.draw.circle(surface, GREEN, (int(self.x), int(self.y)), self.radius)
            # Draw eyes
            pygame.draw.circle(surface, WHITE, (int(self.x - 8), int(self.y - 5)), 6)
            pygame.draw.circle(surface, WHITE, (int(self.x + 8), int(self.y - 5)), 6)
            pygame.draw.circle(surface, BLACK, (int(self.x - 8), int(self.y - 5)), 3)
            pygame.draw.circle(surface, BLACK, (int(self.x + 8), int(self.y - 5)), 3)
            # Draw nose
            pygame.draw.circle(surface, (0, 100, 0), (int(self.x), int(self.y + 5)), 8)
            pygame.draw.circle(surface, BLACK, (int(self.x - 3), int(self.y + 5)), 2)
            pygame.draw.circle(surface, BLACK, (int(self.x + 3), int(self.y + 5)), 2)
    
    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.destroyed = True
            return True
        return False

def create_level(level_num):
    global blocks, pigs, birds, bird_launched, trajectory_points, power, angle, game_state, birds_left
    
    blocks = []
    pigs = []
    birds = []
    bird_launched = False
    trajectory_points = []
    power = 0
    angle = 0
    game_state = "aiming"
    birds_left = 3
    
    # Create birds
    for i in range(birds_left):
        birds.append(Bird(100 + i * 30, HEIGHT - 150))
    
    # Create slingshot bird
    birds[0].x, birds[0].y = slingshot_pos
    
    # Level 1 layout
    if level_num == 1:
        # Ground blocks
        blocks.append(Block(600, HEIGHT - 140, 80, 40, "wood"))
        blocks.append(Block(700, HEIGHT - 140, 80, 40, "wood"))
        blocks.append(Block(800, HEIGHT - 140, 80, 40, "wood"))
        
        # Tower 1
        blocks.append(Block(620, HEIGHT - 200, 20, 60, "wood"))
        blocks.append(Block(680, HEIGHT - 200, 20, 60, "wood"))
        blocks.append(Block(630, HEIGHT - 220, 60, 20, "wood"))
        
        # Tower 2
        blocks.append(Block(720, HEIGHT - 200, 20, 60, "stone"))
        blocks.append(Block(780, HEIGHT - 200, 20, 60, "stone"))
        blocks.append(Block(730, HEIGHT - 220, 60, 20, "stone"))
        
        # Pigs
        pigs.append(Pig(650, HEIGHT - 160))
        pigs.append(Pig(750, HEIGHT - 160))
        pigs.append(Pig(700, HEIGHT - 240))

def draw_sling():
    # Draw slingshot
    pygame.draw.line(screen, BROWN, (slingshot_pos[0] - 20, slingshot_pos[1] + 30), 
                     (slingshot_pos[0] - 20, slingshot_pos[1] - 50), 8)
    pygame.draw.line(screen, BROWN, (slingshot_pos[0] + 20, slingshot_pos[1] + 30), 
                     (slingshot_pos[0] + 20, slingshot_pos[1] - 50), 8)
    pygame.draw.line(screen, BROWN, (slingshot_pos[0] - 20, slingshot_pos[1] - 50), 
                     (slingshot_pos[0] + 20, slingshot_pos[1] - 50), 8)

def draw_trajectory():
    if game_state == "aiming" and len(trajectory_points) > 1:
        pygame.draw.lines(screen, YELLOW, False, trajectory_points, 2)

def draw_power_bar():
    if game_state == "aiming":
        pygame.draw.rect(screen, WHITE, (20, 20, 200, 30), 2)
        pygame.draw.rect(screen, RED, (22, 22, power * 6.6, 26))

def draw_ui():
    # Score
    font = pygame.font.SysFont(None, 48)
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (WIDTH - 200, 20))
    
    # Birds left
    bird_text = font.render(f"Birds: {birds_left}", True, WHITE)
    screen.blit(bird_text, (WIDTH - 200, 70))
    
    # Level
    level_text = font.render(f"Level: {level}", True, WHITE)
    screen.blit(level_text, (WIDTH - 200, 120))
    
    # Instructions
    font_small = pygame.font.SysFont(None, 28)
    if game_state == "aiming":
        inst_text = font_small.render("Drag and release to launch bird", True, WHITE)
        screen.blit(inst_text, (WIDTH//2 - inst_text.get_width()//2, 20))
    elif game_state == "game_over":
        over_text = font.render("GAME OVER! Press R to restart", True, RED)
        screen.blit(over_text, (WIDTH//2 - over_text.get_width()//2, HEIGHT//2))

def check_collisions():
    global score
    
    active_bird = None
    for bird in birds:
        if bird.launched and not bird.destroyed:
            active_bird = bird
            break
            
    if not active_bird:
        return
    
    # Check bird-block collisions
    for block in blocks:
        if not block.destroyed and active_bird.check_collision(block):
            # Calculate damage based on bird speed
            speed = math.sqrt(active_bird.vx**2 + active_bird.vy**2)
            damage = min(100, max(10, speed * 2))
            
            if block.take_damage(damage):
                score += 50
            
            # Bounce effect
            active_bird.vx *= -0.5
            active_bird.vy *= -0.5
    
    # Check bird-pig collisions
    for pig in pigs:
        if not pig.destroyed:
            dx = pig.x - active_bird.x
            dy = pig.y - active_bird.y
            distance = math.sqrt(dx**2 + dy**2)
            
            if distance < pig.radius + active_bird.radius:
                # Calculate damage based on bird speed
                speed = math.sqrt(active_bird.vx**2 + active_bird.vy**2)
                damage = min(100, max(20, speed * 3))
                
                if pig.take_damage(damage):
                    score += 100
                
                # Bounce effect
                active_bird.vx *= -0.7
                active_bird.vy *= -0.7

def check_win_condition():
    # Check if all pigs are destroyed
    for pig in pigs:
        if not pig.destroyed:
            return False
    return True

def check_lose_condition():
    # Check if no birds left and no active bird
    active_bird = False
    for bird in birds:
        if not bird.destroyed:
            active_bird = True
            break
    
    if not active_bird and birds_left <= 0:
        return True
    return False

# Create initial level
create_level(level)

# Main game loop
running = True
while running:
    mouse_x, mouse_y = pygame.mouse.get_pos()
    
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                create_level(level)
            if event.key == pygame.K_ESCAPE:
                running = False
                
        if game_state == "aiming":
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Check if clicking on the bird
                bird = birds[0] if birds else None
                if bird and not bird.launched:
                    dx = bird.x - mouse_x
                    dy = bird.y - mouse_y
                    distance = math.sqrt(dx**2 + dy**2)
                    if distance < bird.radius:
                        bird.dragging = True
                        
            if event.type == pygame.MOUSEBUTTONUP:
                bird = birds[0] if birds else None
                if bird and bird.dragging:
                    bird.dragging = False
                    # Calculate launch power and angle
                    dx = bird.start_x - bird.x
                    dy = bird.start_y - bird.y
                    power = min(max_power, math.sqrt(dx**2 + dy**2) / 5)
                    angle = math.atan2(dy, dx)
                    bird.launch(power, angle)
                    bird_launched = True
                    game_state = "flying"
                    
    # Update dragging bird position
    if game_state == "aiming" and birds and birds[0].dragging:
        bird = birds[0]
        bird.x = mouse_x
        bird.y = mouse_y
        
        # Calculate trajectory
        trajectory_points = []
        power = min(max_power, math.sqrt((bird.start_x - bird.x)**2 + (bird.start_y - bird.y)**2) / 5)
        angle = math.atan2(bird.start_y - bird.y, bird.start_x - bird.x)
        
        # Simulate trajectory
        temp_x, temp_y = bird.start_x, bird.start_y
        temp_vx = power * math.cos(angle)
        temp_vy = power * math.sin(angle)
        
        for _ in range(30):
            trajectory_points.append((temp_x, temp_y))
            temp_vy += GRAVITY
            temp_x += temp_vx
            temp_y += temp_vy
            
            # Stop if hit ground
            if temp_y > HEIGHT - 100:
                break
    
    # Update game objects
    if game_state == "flying":
        # Update birds
        all_birds_destroyed = True
        for bird in birds:
            if bird.update():
                # Bird went out of bounds, remove it
                if bird.launched:
                    birds_left -= 1
            if not bird.destroyed:
                all_birds_destroyed = False
                
        # Check collisions
        check_collisions()
        
        # Check win/lose conditions
        if check_win_condition():
            level += 1
            create_level(level)
        elif check_lose_condition():
            game_state = "game_over"
    
    # Drawing
    # Sky background
    screen.fill(SKY_BLUE)
    
    # Clouds
    for i in range(5):
        cloud_x = (pygame.time.get_ticks() // 50 + i * 200) % (WIDTH + 400) - 200
        pygame.draw.circle(screen, WHITE, (cloud_x, 100), 30)
        pygame.draw.circle(screen, WHITE, (cloud_x + 20, 90), 35)
        pygame.draw.circle(screen, WHITE, (cloud_x + 40, 100), 30)
        pygame.draw.circle(screen, WHITE, (cloud_x + 20, 110), 25)
    
    # Ground
    pygame.draw.rect(screen, GROUND_GREEN, (0, HEIGHT - 100, WIDTH, 100))
    
    # Draw blocks
    for block in blocks:
        block.draw(screen)
    
    # Draw pigs
    for pig in pigs:
        pig.draw(screen)
    
    # Draw slingshot
    draw_sling()
    
    # Draw trajectory
    draw_trajectory()
    
    # Draw birds
    for bird in birds:
        bird.draw(screen)
    
    # Draw power bar
    draw_power_bar()
    
    # Draw UI
    draw_ui()
    
    pygame.display.flip()
    clock = pygame.time.Clock()
    clock.tick(60)

pygame.quit()
sys.exit()