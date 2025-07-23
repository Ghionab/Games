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
PINK = (255, 182, 193)

# Physics constants
GRAVITY = 0.5
FRICTION = 0.99
ELASTICITY = 0.7
DAMPING = 0.98

# Game variables
score = 0
birds = []
blocks = []
pigs = []
slingshot_pos = (150, HEIGHT - 200)
bird_radius = 20
trajectory_points = []
power = 0
angle = 0
max_power = 30
game_state = "aiming"  # aiming, flying, game_over
level = 1
birds_left = 5
current_bird_index = 0

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
        self.trail = []  # For visual trail effect
        
    def draw(self, surface):
        if not self.destroyed:
            # Draw trail
            for i, pos in enumerate(self.trail):
                alpha = int(255 * (i / len(self.trail)))
                radius = int(self.radius * (i / len(self.trail)))
                pygame.draw.circle(surface, (self.color[0], self.color[1], self.color[2], alpha), 
                                  (int(pos[0]), int(pos[1])), max(1, radius))
            
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
            # Add current position to trail
            self.trail.append((self.x, self.y))
            if len(self.trail) > 10:
                self.trail.pop(0)
            
            # Apply gravity
            self.vy += GRAVITY
            
            # Apply air resistance
            self.vx *= DAMPING
            self.vy *= DAMPING
            
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
                self.vx *= 0.8  # Extra friction on ground
                
                # Stop if moving very slowly
                if abs(self.vx) < 0.5 and abs(self.vy) < 0.5:
                    self.vx = 0
                    self.vy = 0
                    
            # Check if bird is out of bounds or stopped
            if (self.x < -100 or self.x > WIDTH + 100 or 
                self.y > HEIGHT + 100 or 
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
            
        # Circle-rectangle collision
        test_x = self.x
        test_y = self.y
        
        if self.x < obj.x:
            test_x = obj.x
        elif self.x > obj.x + obj.width:
            test_x = obj.x + obj.width
            
        if self.y < obj.y:
            test_y = obj.y
        elif self.y > obj.y + obj.height:
            test_y = obj.y + obj.height
            
        dist_x = self.x - test_x
        dist_y = self.y - test_y
        distance = math.sqrt(dist_x * dist_x + dist_y * dist_y)
        
        return distance <= self.radius

class Block:
    def __init__(self, x, y, width, height, material="wood"):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.material = material
        self.health = 100
        self.destroyed = False
        self.rotation = 0
        self.angular_velocity = 0
        
        if material == "wood":
            self.color = BROWN
            self.density = 0.5
        elif material == "stone":
            self.color = GRAY
            self.density = 1.0
        elif material == "ice":
            self.color = BLUE
            self.density = 0.3
            
    def draw(self, surface):
        if not self.destroyed:
            # Save the current transform
            block_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            pygame.draw.rect(block_surface, self.color, (0, 0, self.width, self.height))
            pygame.draw.rect(block_surface, DARK_GRAY, (0, 0, self.width, self.height), 2)
            
            # Draw cracks if damaged
            if self.health < 70:
                pygame.draw.line(block_surface, BLACK, (0, self.height//2), 
                                (self.width, self.height//2), 2)
            if self.health < 40:
                pygame.draw.line(block_surface, BLACK, (self.width//2, 0), 
                                (self.width//2, self.height), 2)
            
            # Rotate and draw
            rotated = pygame.transform.rotate(block_surface, self.rotation)
            rect = rotated.get_rect(center=(self.x + self.width//2, self.y + self.height//2))
            surface.blit(rotated, rect.topleft)
    
    def take_damage(self, amount):
        self.health -= amount
        self.angular_velocity += random.uniform(-5, 5)
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
        self.vx = 0
        self.vy = 0
        
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
    global blocks, pigs, birds, bird_launched, trajectory_points, power, angle, game_state, birds_left, current_bird_index
    
    blocks = []
    pigs = []
    birds = []
    bird_launched = False
    trajectory_points = []
    power = 0
    angle = 0
    game_state = "aiming"
    birds_left = 5
    current_bird_index = 0
    
    # Create birds
    for i in range(birds_left):
        birds.append(Bird(80 + i * 30, HEIGHT - 150))
    
    # Create slingshot bird
    if birds:
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
        
        # Tower 3
        blocks.append(Block(820, HEIGHT - 200, 20, 60, "ice"))
        blocks.append(Block(880, HEIGHT - 200, 20, 60, "ice"))
        blocks.append(Block(830, HEIGHT - 220, 60, 20, "ice"))
        
        # Pigs
        pigs.append(Pig(650, HEIGHT - 160))
        pigs.append(Pig(750, HEIGHT - 160))
        pigs.append(Pig(850, HEIGHT - 160))
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

def draw_birds_available():
    font = pygame.font.SysFont(None, 36)
    bird_text = font.render(f"Birds: {birds_left}", True, WHITE)
    screen.blit(bird_text, (20, 60))
    
    # Draw bird icons
    for i in range(birds_left):
        pygame.draw.circle(screen, RED, (30 + i * 25, 100), 10)

def draw_ui():
    # Score
    font = pygame.font.SysFont(None, 48)
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (WIDTH - 200, 20))
    
    # Level
    level_text = font.render(f"Level: {level}", True, WHITE)
    screen.blit(level_text, (WIDTH - 200, 70))
    
    # Instructions
    font_small = pygame.font.SysFont(None, 28)
    if game_state == "aiming":
        inst_text = font_small.render("Drag and release to launch bird", True, WHITE)
        screen.blit(inst_text, (WIDTH//2 - inst_text.get_width()//2, 20))
    elif game_state == "game_over":
        over_text = font.render("GAME OVER! Press R to restart", True, RED)
        screen.blit(over_text, (WIDTH//2 - over_text.get_width()//2, HEIGHT//2))
    elif game_state == "level_complete":
        complete_text = font.render("LEVEL COMPLETE! Press N for next level", True, GREEN)
        screen.blit(complete_text, (WIDTH//2 - complete_text.get_width()//2, HEIGHT//2))

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
            damage = min(100, max(10, speed * block.density * 2))
            
            if block.take_damage(damage):
                score += 50
            
            # Transfer some momentum to the block
            block.vx = active_bird.vx * 0.1
            block.vy = active_bird.vy * 0.1
            
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
                
                # Transfer momentum to pig
                pig.vx = active_bird.vx * 0.5
                pig.vy = active_bird.vy * 0.5
                
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

def next_bird():
    global current_bird_index, game_state
    
    # Mark current bird as destroyed if it's still active
    if current_bird_index < len(birds):
        birds[current_bird_index].destroyed = True
    
    # Move to next bird
    current_bird_index += 1
    
    # Check if we have more birds
    if current_bird_index < len(birds):
        # Position next bird in slingshot
        birds[current_bird_index].x, birds[current_bird_index].y = slingshot_pos
        game_state = "aiming"
    else:
        # No more birds
        if check_lose_condition():
            game_state = "game_over"

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
            if event.key == pygame.K_n and game_state == "level_complete":
                level += 1
                create_level(level)
            if event.key == pygame.K_ESCAPE:
                running = False
                
        if game_state == "aiming":
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Check if clicking on the bird
                if current_bird_index < len(birds):
                    bird = birds[current_bird_index]
                    if not bird.launched:
                        dx = bird.x - mouse_x
                        dy = bird.y - mouse_y
                        distance = math.sqrt(dx**2 + dy**2)
                        if distance < bird.radius:
                            bird.dragging = True
                            
            if event.type == pygame.MOUSEBUTTONUP:
                if current_bird_index < len(birds):
                    bird = birds[current_bird_index]
                    if bird.dragging:
                        bird.dragging = False
                        # Calculate launch power and angle
                        dx = bird.start_x - bird.x
                        dy = bird.start_y - bird.y
                        power = min(max_power, math.sqrt(dx**2 + dy**2) / 5)
                        angle = math.atan2(dy, dx)
                        bird.launch(power, angle)
                        bird_launched = True
                        birds_left -= 1
                        game_state = "flying"
    
    # Update dragging bird position
    if game_state == "aiming" and current_bird_index < len(birds):
        bird = birds[current_bird_index]
        if bird.dragging:
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
            
            for _ in range(50):
                trajectory_points.append((temp_x, temp_y))
                temp_vy += GRAVITY * 0.5  # Reduced gravity for preview
                temp_x += temp_vx
                temp_y += temp_vy
                
                # Stop if hit ground
                if temp_y > HEIGHT - 100:
                    break
    
    # Update game objects
    if game_state == "flying":
        # Update birds
        active_bird_exists = False
        for bird in birds:
            if bird.update():
                # Bird went out of bounds, remove it
                if bird.launched:
                    pass  # Already decremented birds_left
            if not bird.destroyed and bird.launched:
                active_bird_exists = True
                
        # If no active bird, go to next bird
        if not active_bird_exists:
            next_bird()
                
        # Update blocks
        for block in blocks:
            if not block.destroyed:
                block.rotation += block.angular_velocity
                block.angular_velocity *= 0.95  # Slow down rotation
                
                # Apply gravity to blocks that are not supported
                block.vy += GRAVITY * 0.1
                block.x += block.vx
                block.y += block.vy
                
                # Apply damping
                block.vx *= 0.98
                block.vy *= 0.98
                
                # Ground collision for blocks
                if block.y + block.height > HEIGHT - 100:
                    block.y = HEIGHT - 100 - block.height
                    block.vy = 0
                    
        # Update pigs
        for pig in pigs:
            if not pig.destroyed:
                # Apply gravity
                pig.vy += GRAVITY * 0.3
                pig.x += pig.vx
                pig.y += pig.vy
                
                # Apply damping
                pig.vx *= 0.95
                pig.vy *= 0.95
                
                # Ground collision for pigs
                if pig.y + pig.radius > HEIGHT - 100:
                    pig.y = HEIGHT - 100 - pig.radius
                    pig.vy = 0
        
        # Check collisions
        check_collisions()
        
        # Check win/lose conditions
        if check_win_condition():
            game_state = "level_complete"
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
    
    # Draw birds available
    draw_birds_available()
    
    # Draw UI
    draw_ui()
    
    pygame.display.flip()
    clock = pygame.time.Clock()
    clock.tick(60)

pygame.quit()
sys.exit()