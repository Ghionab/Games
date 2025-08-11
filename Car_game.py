import pygame
import random
import sys
import math

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
RED = (255, 50, 50)
GREEN = (50, 200, 50)
BLUE = (50, 100, 255)
GRAY = (100, 100, 100)
LIGHT_GRAY = (200, 200, 200)
YELLOW = (255, 255, 0)
DARK_GREEN = (0, 120, 0)
ORANGE = (255, 165, 0)
PURPLE = (180, 70, 220)
SKY_BLUE = (135, 206, 235)

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Enhanced Car Racing Game")
clock = pygame.time.Clock()

# Font
font = pygame.font.SysFont('Arial', 24)
big_font = pygame.font.SysFont('Arial', 48)
small_font = pygame.font.SysFont('Arial', 20)

# Try to initialize sound, but handle if it fails
try:
    pygame.mixer.init()
    sound_enabled = True
except:
    sound_enabled = False

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
        self.invincible = False
        self.invincible_timer = 0
        self.shield_active = False
        self.shield_timer = 0
        
    def move_left(self):
        if self.lane > 0:
            self.lane -= 1
            self.target_x = self.lane_positions[self.lane]
            if sound_enabled:
                # Simple beep effect
                try:
                    pygame.mixer.Sound.play(pygame.mixer.Sound(buffer=bytearray([128]*4410)))
                except:
                    pass
    
    def move_right(self):
        if self.lane < 2:
            self.lane += 1
            self.target_x = self.lane_positions[self.lane]
            if sound_enabled:
                # Simple beep effect
                try:
                    pygame.mixer.Sound.play(pygame.mixer.Sound(buffer=bytearray([128]*4410)))
                except:
                    pass
            
    def activate_shield(self):
        self.shield_active = True
        self.shield_timer = 300  # 5 seconds at 60 FPS
            
    def update(self):
        # Smooth movement to target lane
        if self.x < self.target_x:
            self.x += min(self.speed, self.target_x - self.x)
        elif self.x > self.target_x:
            self.x -= min(self.speed, self.x - self.target_x)
            
        # Update invincibility timer
        if self.invincible:
            self.invincible_timer -= 1
            if self.invincible_timer <= 0:
                self.invincible = False
                
        # Update shield timer
        if self.shield_active:
            self.shield_timer -= 1
            if self.shield_timer <= 0:
                self.shield_active = False
            
    def draw(self):
        # Car body with gradient effect
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height), border_radius=12)
        
        # Car top
        pygame.draw.rect(screen, self.color, (self.x + 5, self.y - 15, self.width - 10, 20), border_radius=7)
        
        # Windows
        window_color = (180, 220, 255) if not self.invincible else YELLOW
        pygame.draw.rect(screen, window_color, (self.x + 10, self.y - 10, self.width - 20, 15), border_radius=3)
        pygame.draw.rect(screen, window_color, (self.x + 10, self.y + 10, self.width - 20, 20), border_radius=3)
        
        # Wheels
        wheel_color = BLACK if not self.invincible else YELLOW
        pygame.draw.rect(screen, wheel_color, (self.x - 3, self.y + 10, 6, 20), border_radius=3)
        pygame.draw.rect(screen, wheel_color, (self.x + self.width - 3, self.y + 10, 6, 20), border_radius=3)
        pygame.draw.rect(screen, wheel_color, (self.x - 3, self.y + self.height - 30, 6, 20), border_radius=3)
        pygame.draw.rect(screen, wheel_color, (self.x + self.width - 3, self.y + self.height - 30, 6, 20), border_radius=3)
        
        # Headlights
        pygame.draw.circle(screen, YELLOW, (self.x + 10, self.y + self.height - 5), 5)
        pygame.draw.circle(screen, YELLOW, (self.x + self.width - 10, self.y + self.height - 5), 5)
        
        # Shield effect
        if self.shield_active:
            shield_radius = self.width + 15
            pygame.draw.circle(screen, (100, 200, 255, 100), 
                              (self.x + self.width//2, self.y + self.height//2), 
                              shield_radius, 3)
            # Draw rotating shield particles
            for i in range(8):
                angle = (pygame.time.get_ticks() / 10 + i * 45) % 360
                rad = math.radians(angle)
                x = self.x + self.width//2 + shield_radius * math.cos(rad)
                y = self.y + self.height//2 + shield_radius * math.sin(rad)
                pygame.draw.circle(screen, (100, 200, 255), (x, y), 5)

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
        self.speed = random.randint(5, 8)
        self.color = random.choice([BLUE, GREEN, PURPLE])
        self.passed = False
        self.wobble = 0
        self.wobble_direction = random.choice([-1, 1])
        
    def update(self, game_speed):
        self.y += self.speed + game_speed
        self.wobble += 0.1 * self.wobble_direction
        if abs(self.wobble) > 2:
            self.wobble_direction *= -1
            
    def draw(self):
        # Apply wobble effect
        x_offset = self.wobble * 2
        actual_x = self.x + x_offset
        
        # Car body
        pygame.draw.rect(screen, self.color, (actual_x, self.y, self.width, self.height), border_radius=12)
        
        # Car top
        pygame.draw.rect(screen, self.color, (actual_x + 5, self.y - 15, self.width - 10, 20), border_radius=7)
        
        # Windows
        pygame.draw.rect(screen, LIGHT_GRAY, (actual_x + 10, self.y - 10, self.width - 20, 15), border_radius=3)
        pygame.draw.rect(screen, LIGHT_GRAY, (actual_x + 10, self.y + 10, self.width - 20, 20), border_radius=3)
        
        # Wheels
        pygame.draw.rect(screen, BLACK, (actual_x - 3, self.y + 10, 6, 20), border_radius=3)
        pygame.draw.rect(screen, BLACK, (actual_x + self.width - 3, self.y + 10, 6, 20), border_radius=3)
        pygame.draw.rect(screen, BLACK, (actual_x - 3, self.y + self.height - 30, 6, 20), border_radius=3)
        pygame.draw.rect(screen, BLACK, (actual_x + self.width - 3, self.y + self.height - 30, 6, 20), border_radius=3)

class PowerUp:
    def __init__(self, lane):
        self.width = 30
        self.height = 30
        self.lane = lane
        self.lane_positions = [
            SCREEN_WIDTH // 2 - ROAD_WIDTH // 2 + LANE_WIDTH // 2 - self.width // 2,
            SCREEN_WIDTH // 2 - self.width // 2,
            SCREEN_WIDTH // 2 + ROAD_WIDTH // 2 - LANE_WIDTH // 2 - self.width // 2
        ]
        self.x = self.lane_positions[self.lane]
        self.y = -self.height
        self.speed = 5
        self.type = random.choice(["shield", "slow", "points"])
        self.colors = {
            "shield": (100, 200, 255),
            "slow": (255, 165, 0),
            "points": (255, 215, 0)
        }
        self.rotation = 0
        
    def update(self, game_speed):
        self.y += self.speed + game_speed
        self.rotation = (self.rotation + 5) % 360
        
    def draw(self):
        center_x = self.x + self.width // 2
        center_y = self.y + self.height // 2
        
        # Draw rotating power-up
        if self.type == "shield":
            points = []
            for i in range(5):
                angle = math.radians(self.rotation + i * 72)
                x = center_x + 15 * math.cos(angle)
                y = center_y + 15 * math.sin(angle)
                points.append((x, y))
            pygame.draw.polygon(screen, self.colors[self.type], points)
            
        elif self.type == "slow":
            pygame.draw.circle(screen, self.colors[self.type], (center_x, center_y), 15)
            pygame.draw.rect(screen, WHITE, (center_x - 10, center_y - 3, 20, 6))
            
        elif self.type == "points":
            pygame.draw.circle(screen, self.colors[self.type], (center_x, center_y), 15)
            pygame.draw.circle(screen, WHITE, (center_x, center_y), 5)

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.size = random.randint(2, 6)
        self.speed_x = random.randint(-3, 3)
        self.speed_y = random.randint(-3, 3)
        self.life = 30
        
    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y
        self.life -= 1
        self.size = max(0, self.size - 0.1)
        
    def draw(self):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), int(self.size))

class Game:
    def __init__(self):
        self.player = PlayerCar()
        self.obstacles = []
        self.powerups = []
        self.particles = []
        self.score = 0
        self.game_speed = 5
        self.last_obstacle_time = pygame.time.get_ticks()
        self.last_powerup_time = pygame.time.get_ticks()
        self.obstacle_frequency = 1500  # milliseconds
        self.powerup_frequency = 5000  # milliseconds
        self.game_over = False
        self.road_markings_y = 0
        self.distance = 0
        self.slow_motion = False
        self.slow_motion_timer = 0
        self.background_offset = 0
        self.clouds = []
        for _ in range(5):
            self.clouds.append({
                'x': random.randint(0, SCREEN_WIDTH),
                'y': random.randint(50, 200),
                'speed': random.uniform(0.5, 1.5),
                'size': random.randint(40, 80)
            })
        
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
                if event.key == pygame.K_s and not self.game_over:
                    self.player.activate_shield()
                    
    def update(self):
        if self.game_over:
            return
            
        current_time = pygame.time.get_ticks()
        
        # Update player
        self.player.update()
        
        # Update background
        self.background_offset = (self.background_offset + self.game_speed/10) % 20
        
        # Update clouds
        for cloud in self.clouds:
            cloud['x'] -= cloud['speed']
            if cloud['x'] < -100:
                cloud['x'] = SCREEN_WIDTH + 50
                cloud['y'] = random.randint(50, 200)
        
        # Update road markings
        self.road_markings_y += self.game_speed
        if self.road_markings_y > 40:
            self.road_markings_y = 0
            
        # Update distance
        self.distance += self.game_speed / 10
            
        # Generate new obstacles
        if current_time - self.last_obstacle_time > self.obstacle_frequency:
            lane = random.randint(0, 2)
            self.obstacles.append(Obstacle(lane))
            self.last_obstacle_time = current_time
            
        # Generate new power-ups
        if current_time - self.last_powerup_time > self.powerup_frequency:
            lane = random.randint(0, 2)
            self.powerups.append(PowerUp(lane))
            self.last_powerup_time = current_time
            
        # Update obstacles and check collisions
        for obstacle in self.obstacles[:]:
            obstacle.update(self.game_speed)
            
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
                if self.player.shield_active:
                    # Destroy obstacle with shield
                    self.obstacles.remove(obstacle)
                    self.score += 2
                    # Create particles
                    for _ in range(20):
                        self.particles.append(Particle(
                            obstacle.x + obstacle.width//2,
                            obstacle.y + obstacle.height//2,
                            obstacle.color
                        ))
                    if sound_enabled:
                        try:
                            pygame.mixer.Sound.play(pygame.mixer.Sound(buffer=bytearray([200]*8820)))
                        except:
                            pass
                elif not self.player.invincible:
                    self.game_over = True
                    if sound_enabled:
                        try:
                            pygame.mixer.Sound.play(pygame.mixer.Sound(buffer=bytearray([50]*13230)))
                        except:
                            pass
                    # Create crash particles
                    for _ in range(50):
                        self.particles.append(Particle(
                            self.player.x + self.player.width//2,
                            self.player.y + self.player.height//2,
                            RED
                        ))
                    
        # Update power-ups and check collection
        for powerup in self.powerups[:]:
            powerup.update(self.game_speed)
            
            # Remove power-ups that are off screen
            if powerup.y > SCREEN_HEIGHT:
                self.powerups.remove(powerup)
                continue
                
            # Check collection
            player_rect = pygame.Rect(self.player.x, self.player.y, self.player.width, self.player.height)
            powerup_rect = pygame.Rect(powerup.x, powerup.y, powerup.width, powerup.height)
            
            if player_rect.colliderect(powerup_rect):
                self.powerups.remove(powerup)
                if sound_enabled:
                    try:
                        pygame.mixer.Sound.play(pygame.mixer.Sound(buffer=bytearray([180]*4410)))
                    except:
                        pass
                
                if powerup.type == "shield":
                    self.player.activate_shield()
                elif powerup.type == "slow":
                    self.slow_motion = True
                    self.slow_motion_timer = 300  # 5 seconds
                elif powerup.type == "points":
                    self.score += 10
                    
                # Create collection particles
                for _ in range(15):
                    self.particles.append(Particle(
                        powerup.x + powerup.width//2,
                        powerup.y + powerup.height//2,
                        powerup.colors[powerup.type]
                    ))
        
        # Update particles
        for particle in self.particles[:]:
            particle.update()
            if particle.life <= 0:
                self.particles.remove(particle)
                
        # Update slow motion timer
        if self.slow_motion:
            self.slow_motion_timer -= 1
            if self.slow_motion_timer <= 0:
                self.slow_motion = False
                
        # Increase difficulty over time
        self.game_speed = 5 + self.score // 20
        self.obstacle_frequency = max(500, 1500 - self.score * 5)
        
    def draw(self):
        # Draw sky background
        screen.fill(SKY_BLUE)
        
        # Draw sun
        pygame.draw.circle(screen, (255, 255, 200), (700, 80), 60)
        
        # Draw clouds
        for cloud in self.clouds:
            pygame.draw.circle(screen, WHITE, (cloud['x'], cloud['y']), cloud['size']//2)
            pygame.draw.circle(screen, WHITE, (cloud['x'] + cloud['size']//3, cloud['y'] - cloud['size']//4), cloud['size']//2)
            pygame.draw.circle(screen, WHITE, (cloud['x'] + cloud['size']//3, cloud['y'] + cloud['size']//4), cloud['size']//2)
            pygame.draw.circle(screen, WHITE, (cloud['x'] + cloud['size']//1.5, cloud['y']), cloud['size']//2)
        
        # Draw distant hills
        for i in range(5):
            pygame.draw.ellipse(screen, DARK_GREEN, (i * 200 - 50, SCREEN_HEIGHT - 200, 300, 150))
        
        # Draw road
        road_x = SCREEN_WIDTH // 2 - ROAD_WIDTH // 2
        pygame.draw.rect(screen, GRAY, (road_x, 0, ROAD_WIDTH, SCREEN_HEIGHT))
        
        # Draw road markings with offset for movement effect
        for y in range(-40, SCREEN_HEIGHT, 40):
            pygame.draw.rect(screen, YELLOW, (SCREEN_WIDTH // 2 - 5, y + self.road_markings_y, 10, 20))
            
        # Draw road borders
        pygame.draw.rect(screen, WHITE, (road_x - 5, 0, 5, SCREEN_HEIGHT))
        pygame.draw.rect(screen, WHITE, (road_x + ROAD_WIDTH, 0, 5, SCREEN_HEIGHT))
        
        # Draw lane markings with offset for movement effect
        for i in range(1, 3):
            lane_x = road_x + i * LANE_WIDTH
            for y in range(0, SCREEN_HEIGHT, 40):
                pygame.draw.rect(screen, WHITE, (lane_x - 2, y + self.background_offset, 4, 20))
        
        # Draw particles
        for particle in self.particles:
            particle.draw()
        
        # Draw player car
        self.player.draw()
        
        # Draw obstacles
        for obstacle in self.obstacles:
            obstacle.draw()
            
        # Draw power-ups
        for powerup in self.powerups:
            powerup.draw()
            
        # Draw UI panel
        pygame.draw.rect(screen, (50, 50, 50, 180), (0, 0, SCREEN_WIDTH, 40))
        
        # Draw score
        score_text = font.render(f"Score: {self.score}", True, WHITE)
        screen.blit(score_text, (20, 10))
        
        # Draw distance
        distance_text = font.render(f"Distance: {int(self.distance)}m", True, WHITE)
        screen.blit(distance_text, (180, 10))
        
        # Draw speed
        speed_text = font.render(f"Speed: {self.game_speed} km/h", True, WHITE)
        screen.blit(speed_text, (380, 10))
        
        # Draw shield indicator
        if self.player.shield_active:
            shield_time = self.player.shield_timer // 60
            shield_text = font.render(f"Shield: {shield_time}s", True, (100, 200, 255))
            screen.blit(shield_text, (SCREEN_WIDTH - 150, 10))
            
        # Draw slow motion indicator
        if self.slow_motion:
            slow_time = self.slow_motion_timer // 60
            slow_text = font.render(f"SLOW: {slow_time}s", True, ORANGE)
            screen.blit(slow_text, (SCREEN_WIDTH - 300, 10))
            
        # Draw controls hint
        controls_text = small_font.render("Controls: A/D or ←/→ to move, S for shield", True, WHITE)
        screen.blit(controls_text, (SCREEN_WIDTH // 2 - controls_text.get_width() // 2, SCREEN_HEIGHT - 30))
        
        # Draw game over message
        if self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))
            
            game_over_text = big_font.render("GAME OVER", True, RED)
            screen.blit(game_over_text, (SCREEN_WIDTH//2 - game_over_text.get_width()//2, SCREEN_HEIGHT//2 - 80))
            
            score_text = font.render(f"Final Score: {self.score}", True, WHITE)
            screen.blit(score_text, (SCREEN_WIDTH//2 - score_text.get_width()//2, SCREEN_HEIGHT//2 - 10))
            
            distance_text = font.render(f"Distance Traveled: {int(self.distance)}m", True, WHITE)
            screen.blit(distance_text, (SCREEN_WIDTH//2 - distance_text.get_width()//2, SCREEN_HEIGHT//2 + 30))
            
            restart_text = font.render("Press SPACE to restart", True, YELLOW)
            screen.blit(restart_text, (SCREEN_WIDTH//2 - restart_text.get_width()//2, SCREEN_HEIGHT//2 + 80))

# Create game instance
game = Game()

# Main game loop
while True:
    game.handle_events()
    game.update()
    game.draw()
    
    pygame.display.flip()
    # Slow down game when in slow motion
    if game.slow_motion:
        clock.tick(FPS // 2)
    else:
        clock.tick(FPS)