import pygame
import random
import sys

# Initialize pygame
pygame.init()

# Game constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
LANE_WIDTH = 200
ROAD_WIDTH = LANE_WIDTH * 3
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (100, 100, 100)
LIGHT_GRAY = (200, 200, 200)
YELLOW = (255, 255, 0)
DARK_GREEN = (0, 120, 0)

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Simple Car Racing Game")
clock = pygame.time.Clock()

# Font
font = pygame.font.SysFont('Arial', 24)
big_font = pygame.font.SysFont('Arial', 48)

class PlayerCar:
    def __init__(self):
        self.width = 50
        self.height = 90
        self.x = SCREEN_WIDTH // 2 - self.width // 2
        self.y = SCREEN_HEIGHT - self.height - 20
        self.speed = 8
        self.color = RED
        self.lane = 1  # 0: left, 1: center, 2: right
        self.lane_positions = [
            SCREEN_WIDTH // 2 - ROAD_WIDTH // 2 + LANE_WIDTH // 2 - self.width // 2,
            SCREEN_WIDTH // 2 - self.width // 2,
            SCREEN_WIDTH // 2 + ROAD_WIDTH // 2 - LANE_WIDTH // 2 - self.width // 2
        ]
        self.target_x = self.lane_positions[self.lane]
        
    def move_left(self):
        if self.lane > 0:
            self.lane -= 1
            self.target_x = self.lane_positions[self.lane]
    
    def move_right(self):
        if self.lane < 2:
            self.lane += 1
            self.target_x = self.lane_positions[self.lane]
            
    def update(self):
        # Smooth movement to target lane
        if self.x < self.target_x:
            self.x += min(self.speed, self.target_x - self.x)
        elif self.x > self.target_x:
            self.x -= min(self.speed, self.x - self.target_x)
            
    def draw(self):
        # Car body
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height), border_radius=10)
        
        # Car top
        pygame.draw.rect(screen, self.color, (self.x + 5, self.y - 15, self.width - 10, 20), border_radius=5)
        
        # Windows
        pygame.draw.rect(screen, LIGHT_GRAY, (self.x + 10, self.y - 10, self.width - 20, 15), border_radius=3)
        pygame.draw.rect(screen, LIGHT_GRAY, (self.x + 10, self.y + 10, self.width - 20, 20), border_radius=3)
        
        # Wheels
        pygame.draw.rect(screen, BLACK, (self.x - 3, self.y + 10, 6, 20), border_radius=3)
        pygame.draw.rect(screen, BLACK, (self.x + self.width - 3, self.y + 10, 6, 20), border_radius=3)
        pygame.draw.rect(screen, BLACK, (self.x - 3, self.y + self.height - 30, 6, 20), border_radius=3)
        pygame.draw.rect(screen, BLACK, (self.x + self.width - 3, self.y + self.height - 30, 6, 20), border_radius=3)
        
        # Headlights
        pygame.draw.circle(screen, YELLOW, (self.x + 10, self.y + self.height - 5), 5)
        pygame.draw.circle(screen, YELLOW, (self.x + self.width - 10, self.y + self.height - 5), 5)

class Obstacle:
    def __init__(self, lane):
        self.width = 50
        self.height = 90
        self.lane = lane
        self.lane_positions = [
            SCREEN_WIDTH // 2 - ROAD_WIDTH // 2 + LANE_WIDTH // 2 - self.width // 2,
            SCREEN_WIDTH // 2 - self.width // 2,
            SCREEN_WIDTH // 2 + ROAD_WIDTH // 2 - LANE_WIDTH // 2 - self.width // 2
        ]
        self.x = self.lane_positions[self.lane]
        self.y = -self.height
        self.speed = 5
        self.color = random.choice([BLUE, GREEN])
        self.passed = False
        
    def update(self):
        self.y += self.speed
        
    def draw(self):
        # Car body
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height), border_radius=10)
        
        # Car top
        pygame.draw.rect(screen, self.color, (self.x + 5, self.y - 15, self.width - 10, 20), border_radius=5)
        
        # Windows
        pygame.draw.rect(screen, LIGHT_GRAY, (self.x + 10, self.y - 10, self.width - 20, 15), border_radius=3)
        pygame.draw.rect(screen, LIGHT_GRAY, (self.x + 10, self.y + 10, self.width - 20, 20), border_radius=3)
        
        # Wheels
        pygame.draw.rect(screen, BLACK, (self.x - 3, self.y + 10, 6, 20), border_radius=3)
        pygame.draw.rect(screen, BLACK, (self.x + self.width - 3, self.y + 10, 6, 20), border_radius=3)
        pygame.draw.rect(screen, BLACK, (self.x - 3, self.y + self.height - 30, 6, 20), border_radius=3)
        pygame.draw.rect(screen, BLACK, (self.x + self.width - 3, self.y + self.height - 30, 6, 20), border_radius=3)

class Game:
    def __init__(self):
        self.player = PlayerCar()
        self.obstacles = []
        self.score = 0
        self.game_speed = 5
        self.last_obstacle_time = pygame.time.get_ticks()
        self.obstacle_frequency = 1500  # milliseconds
        self.game_over = False
        self.road_markings_y = 0
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    self.player.move_left()
                if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    self.player.move_right()
                if event.key == pygame.K_SPACE and self.game_over:
                    self.__init__()  # Reset game
                    
    def update(self):
        if self.game_over:
            return
            
        current_time = pygame.time.get_ticks()
        
        # Update player
        self.player.update()
        
        # Update road markings
        self.road_markings_y += self.game_speed
        if self.road_markings_y > 40:
            self.road_markings_y = 0
            
        # Generate new obstacles
        if current_time - self.last_obstacle_time > self.obstacle_frequency:
            lane = random.randint(0, 2)
            self.obstacles.append(Obstacle(lane))
            self.last_obstacle_time = current_time
            
        # Update obstacles and check collisions
        for obstacle in self.obstacles[:]:
            obstacle.update()
            
            # Remove obstacles that are off screen
            if obstacle.y > SCREEN_HEIGHT:
                self.obstacles.remove(obstacle)
                if not obstacle.passed:
                    self.score += 1
                continue
                
            # Check collision
            player_rect = pygame.Rect(self.player.x, self.player.y, self.player.width, self.player.height)
            obstacle_rect = pygame.Rect(obstacle.x, obstacle.y, obstacle.width, obstacle.height)
            
            if player_rect.colliderect(obstacle_rect):
                self.game_over = True
                
        # Increase difficulty over time
        self.game_speed = 5 + self.score // 10
        self.obstacle_frequency = max(500, 1500 - self.score * 10)
        
    def draw(self):
        # Draw sky
        screen.fill(LIGHT_GRAY)
        
        # Draw distant hills
        for i in range(5):
            pygame.draw.ellipse(screen, DARK_GREEN, (i * 200 - 50, SCREEN_HEIGHT - 200, 300, 150))
        
        # Draw road
        road_x = SCREEN_WIDTH // 2 - ROAD_WIDTH // 2
        pygame.draw.rect(screen, GRAY, (road_x, 0, ROAD_WIDTH, SCREEN_HEIGHT))
        
        # Draw road markings
        for y in range(-40, SCREEN_HEIGHT, 40):
            pygame.draw.rect(screen, YELLOW, (SCREEN_WIDTH // 2 - 5, y + self.road_markings_y, 10, 20))
            
        # Draw road borders
        pygame.draw.rect(screen, WHITE, (road_x - 5, 0, 5, SCREEN_HEIGHT))
        pygame.draw.rect(screen, WHITE, (road_x + ROAD_WIDTH, 0, 5, SCREEN_HEIGHT))
        
        # Draw lane markings
        for i in range(1, 3):
            lane_x = road_x + i * LANE_WIDTH
            for y in range(0, SCREEN_HEIGHT, 40):
                pygame.draw.rect(screen, WHITE, (lane_x - 2, y, 4, 20))
        
        # Draw player car
        self.player.draw()
        
        # Draw obstacles
        for obstacle in self.obstacles:
            obstacle.draw()
            
        # Draw score
        score_text = font.render(f"Score: {self.score}", True, BLACK)
        screen.blit(score_text, (20, 20))
        
        # Draw speed
        speed_text = font.render(f"Speed: {self.game_speed} km/h", True, BLACK)
        screen.blit(speed_text, (20, 50))
        
        # Draw game over message
        if self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))
            
            game_over_text = big_font.render("GAME OVER", True, RED)
            screen.blit(game_over_text, (SCREEN_WIDTH//2 - game_over_text.get_width()//2, SCREEN_HEIGHT//2 - 50))
            
            score_text = font.render(f"Final Score: {self.score}", True, WHITE)
            screen.blit(score_text, (SCREEN_WIDTH//2 - score_text.get_width()//2, SCREEN_HEIGHT//2 + 20))
            
            restart_text = font.render("Press SPACE to restart", True, WHITE)
            screen.blit(restart_text, (SCREEN_WIDTH//2 - restart_text.get_width()//2, SCREEN_HEIGHT//2 + 60))

# Create game instance
game = Game()

# Main game loop
while True:
    game.handle_events()
    game.update()
    game.draw()
    
    pygame.display.flip()
    clock.tick(FPS)