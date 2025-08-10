import pygame
import random
import sys

# Initialize pygame
pygame.init()

# Game constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 400
GROUND_HEIGHT = 100
FPS = 60
GRAVITY = 1
JUMP_FORCE = -20
GAME_SPEED = 5
OBSTACLE_FREQUENCY = 1500  # milliseconds

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (83, 83, 83)
LIGHT_GRAY = (247, 247, 247)

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Chrome T-Rex Game")
clock = pygame.time.Clock()

# Font
font = pygame.font.SysFont('arial', 20)
large_font = pygame.font.SysFont('arial', 40)

class Dinosaur:
    def __init__(self):
        self.width = 44
        self.height = 60
        self.x = 80
        self.y = SCREEN_HEIGHT - GROUND_HEIGHT - self.height
        self.vel_y = 0
        self.jumping = False
        self.ducking = False
        self.duck_height = 30
        self.animation_counter = 0
        self.running = True
        
    def jump(self):
        if not self.jumping:
            self.vel_y = JUMP_FORCE
            self.jumping = True
            
    def duck(self, ducking):
        self.ducking = ducking
        
    def update(self):
        # Apply gravity
        if self.jumping:
            self.y += self.vel_y
            self.vel_y += GRAVITY
            
            # Check if landed
            if self.y >= SCREEN_HEIGHT - GROUND_HEIGHT - self.height:
                self.y = SCREEN_HEIGHT - GROUND_HEIGHT - self.height
                self.jumping = False
                self.vel_y = 0
                
        # Animation
        self.animation_counter = (self.animation_counter + 1) % 10
        
    def draw(self):
        # Draw dinosaur body
        dino_height = self.duck_height if self.ducking else self.height
        dino_y = self.y if not self.ducking else SCREEN_HEIGHT - GROUND_HEIGHT - self.duck_height
        
        pygame.draw.rect(screen, GRAY, (self.x, dino_y, self.width, dino_height))
        
        # Draw dinosaur eye
        eye_x = self.x + self.width - 15
        eye_y = dino_y + 15 if self.ducking else dino_y + 15
        pygame.draw.circle(screen, BLACK, (eye_x, eye_y), 5)
        
        # Draw dinosaur legs (animation)
        leg_offset = 0
        if self.running and not self.jumping:
            leg_offset = 5 if self.animation_counter < 5 else -5
            
        leg_y = dino_y + dino_height
        pygame.draw.rect(screen, GRAY, (self.x + 10, leg_y, 8, 15 + leg_offset))
        pygame.draw.rect(screen, GRAY, (self.x + self.width - 18, leg_y, 8, 15 - leg_offset))

class Obstacle:
    def __init__(self):
        self.width = random.randint(20, 40)
        self.height = random.randint(40, 70)
        self.x = SCREEN_WIDTH
        self.y = SCREEN_HEIGHT - GROUND_HEIGHT - self.height
        self.passed = False
        
    def update(self):
        self.x -= GAME_SPEED
        
    def draw(self):
        pygame.draw.rect(screen, GRAY, (self.x, self.y, self.width, self.height))
        
        # Draw some details on the cactus
        for i in range(3):
            if random.random() > 0.3:
                pygame.draw.rect(screen, GRAY, 
                                (self.x - 5 + random.randint(0, self.width), 
                                 self.y + random.randint(5, self.height - 10), 
                                 5, 10))

class Cloud:
    def __init__(self):
        self.x = SCREEN_WIDTH + random.randint(0, 300)
        self.y = random.randint(50, 150)
        self.speed = random.uniform(0.5, 1.5)
        self.size = random.randint(30, 60)
        
    def update(self):
        self.x -= self.speed
        if self.x < -100:
            self.x = SCREEN_WIDTH + 50
            self.y = random.randint(50, 150)
            
    def draw(self):
        pygame.draw.circle(screen, LIGHT_GRAY, (self.x, self.y), self.size // 2)
        pygame.draw.circle(screen, LIGHT_GRAY, (self.x + self.size // 2, self.y - self.size // 4), self.size // 2)
        pygame.draw.circle(screen, LIGHT_GRAY, (self.x + self.size // 2, self.y + self.size // 4), self.size // 2)
        pygame.draw.circle(screen, LIGHT_GRAY, (self.x + self.size, self.y), self.size // 2)

class Game:
    def __init__(self):
        self.dinosaur = Dinosaur()
        self.obstacles = []
        self.clouds = [Cloud() for _ in range(4)]
        self.score = 0
        self.game_speed = GAME_SPEED
        self.last_obstacle_time = pygame.time.get_ticks()
        self.game_over = False
        self.game_started = False
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                    if not self.game_started:
                        self.game_started = True
                    if self.game_over:
                        self.__init__()  # Reset game
                    else:
                        self.dinosaur.jump()
                        
                if event.key == pygame.K_DOWN:
                    self.dinosaur.duck(True)
                    
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_DOWN:
                    self.dinosaur.duck(False)
                    
    def update(self):
        if not self.game_started or self.game_over:
            return
            
        current_time = pygame.time.get_ticks()
        
        # Update dinosaur
        self.dinosaur.update()
        
        # Update clouds
        for cloud in self.clouds:
            cloud.update()
        
        # Generate new obstacles
        if current_time - self.last_obstacle_time > OBSTACLE_FREQUENCY:
            self.obstacles.append(Obstacle())
            self.last_obstacle_time = current_time
            
        # Update obstacles and check collisions
        for obstacle in self.obstacles[:]:
            obstacle.update()
            
            # Remove obstacles that are off screen
            if obstacle.x + obstacle.width < 0:
                self.obstacles.remove(obstacle)
                continue
                
            # Check collision
            dino_rect = pygame.Rect(
                self.dinosaur.x + 10,
                self.dinosaur.y + (self.dinosaur.height - self.dinosaur.duck_height if self.dinosaur.ducking else 0),
                self.dinosaur.width - 20,
                self.dinosaur.duck_height if self.dinosaur.ducking else self.dinosaur.height
            )
            
            obstacle_rect = pygame.Rect(obstacle.x, obstacle.y, obstacle.width, obstacle.height)
            
            if dino_rect.colliderect(obstacle_rect):
                self.game_over = True
                
            # Update score
            if not obstacle.passed and obstacle.x + obstacle.width < self.dinosaur.x:
                obstacle.passed = True
                self.score += 1
                
        # Increase game speed over time
        self.game_speed = GAME_SPEED + self.score // 100
        for obstacle in self.obstacles:
            obstacle.x -= (self.game_speed - GAME_SPEED)
        
    def draw(self):
        # Draw sky background
        screen.fill(WHITE)
        
        # Draw clouds
        for cloud in self.clouds:
            cloud.draw()
        
        # Draw ground
        pygame.draw.rect(screen, GRAY, (0, SCREEN_HEIGHT - GROUND_HEIGHT, SCREEN_WIDTH, GROUND_HEIGHT))
        
        # Draw ground details
        for i in range(0, SCREEN_WIDTH, 30):
            pygame.draw.line(screen, (100, 100, 100), 
                            (i, SCREEN_HEIGHT - GROUND_HEIGHT + 20), 
                            (i + 15, SCREEN_HEIGHT - GROUND_HEIGHT + 20), 2)
        
        # Draw dinosaur
        self.dinosaur.draw()
        
        # Draw obstacles
        for obstacle in self.obstacles:
            obstacle.draw()
            
        # Draw score
        score_text = font.render(f"Score: {self.score}", True, GRAY)
        screen.blit(score_text, (SCREEN_WIDTH - 150, 20))
        
        # Draw game over message
        if self.game_over:
            game_over_text = large_font.render("GAME OVER", True, GRAY)
            restart_text = font.render("Press SPACE to restart", True, GRAY)
            screen.blit(game_over_text, (SCREEN_WIDTH//2 - game_over_text.get_width()//2, SCREEN_HEIGHT//2 - 50))
            screen.blit(restart_text, (SCREEN_WIDTH//2 - restart_text.get_width()//2, SCREEN_HEIGHT//2 + 10))
            
        # Draw start message
        if not self.game_started:
            start_text = large_font.render("Press SPACE to Start", True, GRAY)
            screen.blit(start_text, (SCREEN_WIDTH//2 - start_text.get_width()//2, SCREEN_HEIGHT//2 - 50))
            
            hint_text = font.render("SPACE: Jump, DOWN: Duck", True, GRAY)
            screen.blit(hint_text, (SCREEN_WIDTH//2 - hint_text.get_width()//2, SCREEN_HEIGHT//2 + 10))

# Create game instance
game = Game()

# Main game loop
while True:
    game.handle_events()
    game.update()
    game.draw()
    
    pygame.display.flip()
    clock.tick(FPS)