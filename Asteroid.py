import pygame
import random
import math

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Asteroids - Simple Version")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 50, 50)
GREEN = (50, 255, 100)
BLUE = (50, 150, 255)
YELLOW = (255, 255, 50)
GRAY = (150, 150, 150)
CYAN = (0, 200, 255)

# Game variables
clock = pygame.time.Clock()
FPS = 30  # Lower FPS for better performance
score = 0
lives = 3
level = 1
game_over = False
game_won = False
font = pygame.font.SysFont(None, 36)

# Player ship class
class Ship:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = HEIGHT // 2
        self.angle = 0
        self.speed_x = 0
        self.speed_y = 0
        self.max_speed = 5
        self.rotation_speed = 5
        self.acceleration = 0.2
        self.friction = 0.98
        self.shoot_delay = 500  # milliseconds
        self.last_shot = 0
        self.invincible = False
        self.invincible_timer = 0
        self.invincible_duration = 3000  # 3 seconds
        
    def update(self):
        # Handle rotation
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.angle += self.rotation_speed
        if keys[pygame.K_RIGHT]:
            self.angle -= self.rotation_speed
            
        # Handle acceleration
        if keys[pygame.K_UP]:
            rad_angle = math.radians(self.angle)
            self.speed_x += self.acceleration * math.sin(rad_angle)
            self.speed_y -= self.acceleration * math.cos(rad_angle)
            
            # Limit speed
            speed = math.sqrt(self.speed_x**2 + self.speed_y**2)
            if speed > self.max_speed:
                self.speed_x = self.speed_x * self.max_speed / speed
                self.speed_y = self.speed_y * self.max_speed / speed
        else:
            # Apply friction
            self.speed_x *= self.friction
            self.speed_y *= self.friction
            
        # Shooting
        if keys[pygame.K_SPACE]:
            self.shoot()
            
        # Update position
        self.x += self.speed_x
        self.y += self.speed_y
        
        # Screen wrapping
        if self.x > WIDTH:
            self.x = 0
        elif self.x < 0:
            self.x = WIDTH
        if self.y > HEIGHT:
            self.y = 0
        elif self.y < 0:
            self.y = HEIGHT
            
        # Update invincibility
        if self.invincible:
            self.invincible_timer -= 1000 / FPS
            if self.invincible_timer <= 0:
                self.invincible = False
                
    def shoot(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot > self.shoot_delay:
            self.last_shot = current_time
            bullets.append(Bullet(self.x, self.y, self.angle))
                
    def respawn(self):
        self.x = WIDTH // 2
        self.y = HEIGHT // 2
        self.speed_x = 0
        self.speed_y = 0
        self.invincible = True
        self.invincible_timer = self.invincible_duration
        
    def draw(self, surface):
        # Draw a simple triangle for the ship
        rad_angle = math.radians(self.angle)
        nose_x = self.x + 20 * math.sin(rad_angle)
        nose_y = self.y - 20 * math.cos(rad_angle)
        
        left_x = self.x + 15 * math.sin(rad_angle + 2.5)
        left_y = self.y - 15 * math.cos(rad_angle + 2.5)
        
        right_x = self.x + 15 * math.sin(rad_angle - 2.5)
        right_y = self.y - 15 * math.cos(rad_angle - 2.5)
        
        # Draw ship
        if not self.invincible or int(pygame.time.get_ticks() / 100) % 2 == 0:
            pygame.draw.polygon(surface, CYAN, [(nose_x, nose_y), (left_x, left_y), (right_x, right_y)], 2)

# Bullet class
class Bullet:
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = 10
        self.life = 60  # Frames before bullet disappears
        
    def update(self):
        # Move bullet in the direction it was fired
        rad_angle = math.radians(self.angle)
        self.x += self.speed * math.sin(rad_angle)
        self.y -= self.speed * math.cos(rad_angle)
        
        # Screen wrapping
        if self.x > WIDTH:
            self.x = 0
        elif self.x < 0:
            self.x = WIDTH
        if self.y > HEIGHT:
            self.y = 0
        elif self.y < 0:
            self.y = HEIGHT
            
        # Decrease life
        self.life -= 1
        return self.life > 0
        
    def draw(self, surface):
        pygame.draw.circle(surface, YELLOW, (int(self.x), int(self.y)), 3)

# Asteroid class
class Asteroid:
    def __init__(self, size="large"):
        self.size = size
        if size == "large":
            self.radius = 40
            self.speed_multiplier = 1
            self.points = 20
        elif size == "medium":
            self.radius = 25
            self.speed_multiplier = 1.5
            self.points = 50
        else:  # small
            self.radius = 15
            self.speed_multiplier = 2
            self.points = 100
            
        # Spawn from outside the screen
        side = random.randint(1, 4)
        if side == 1:  # Top
            self.x = random.randint(0, WIDTH)
            self.y = -self.radius
        elif side == 2:  # Right
            self.x = WIDTH + self.radius
            self.y = random.randint(0, HEIGHT)
        elif side == 3:  # Bottom
            self.x = random.randint(0, WIDTH)
            self.y = HEIGHT + self.radius
        else:  # Left
            self.x = -self.radius
            self.y = random.randint(0, HEIGHT)
            
        # Random movement
        self.speed_x = random.uniform(-1, 1) * self.speed_multiplier
        self.speed_y = random.uniform(-1, 1) * self.speed_multiplier
        self.rotation = 0
        self.rotation_speed = random.uniform(-2, 2)
        
    def update(self):
        # Move asteroid
        self.x += self.speed_x
        self.y += self.speed_y
        
        # Screen wrapping
        if self.x > WIDTH + self.radius:
            self.x = -self.radius
        elif self.x < -self.radius:
            self.x = WIDTH + self.radius
        if self.y > HEIGHT + self.radius:
            self.y = -self.radius
        elif self.y < -self.radius:
            self.y = HEIGHT + self.radius
            
    def break_apart(self):
        # Create smaller asteroids when destroyed
        new_asteroids = []
        if self.size == "large":
            for _ in range(2):
                asteroid = Asteroid("medium")
                asteroid.x = self.x
                asteroid.y = self.y
                new_asteroids.append(asteroid)
        elif self.size == "medium":
            for _ in range(2):
                asteroid = Asteroid("small")
                asteroid.x = self.x
                asteroid.y = self.y
                new_asteroids.append(asteroid)
        return new_asteroids
        
    def draw(self, surface):
        # Draw a simple circle for the asteroid
        pygame.draw.circle(surface, GRAY, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surface, WHITE, (int(self.x), int(self.y)), self.radius, 2)

# Create game objects
ship = Ship()
bullets = []
asteroids = []

# Create initial asteroids
def spawn_asteroids(count):
    for _ in range(count):
        asteroid = Asteroid()
        # Make sure asteroids don't spawn on top of the ship
        while math.sqrt((asteroid.x - ship.x)**2 + (asteroid.y - ship.y)**2) < 100:
            asteroid.x = random.randint(0, WIDTH)
            asteroid.y = random.randint(0, HEIGHT)
        asteroids.append(asteroid)

# Initial asteroid spawn
spawn_asteroids(8)

# Draw stars in the background
stars = []
for _ in range(100):
    x = random.randint(0, WIDTH)
    y = random.randint(0, HEIGHT)
    size = random.randint(1, 3)
    brightness = random.randint(150, 255)
    stars.append([x, y, size, brightness])

# Draw background
def draw_background():
    screen.fill(BLACK)
    
    # Draw stars
    for star in stars:
        pygame.draw.circle(screen, (star[3], star[3], star[3]), (star[0], star[1]), star[2])

# Draw UI elements
def draw_ui():
    # Draw score
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))
    
    # Draw lives
    lives_text = font.render(f"Lives: {lives}", True, WHITE)
    screen.blit(lives_text, (10, 50))
    
    # Draw level
    level_text = font.render(f"Level: {level}", True, WHITE)
    screen.blit(level_text, (10, 90))
    
    # Draw controls
    if not game_over and not game_won:
        ctrl_text = font.render("Arrow Keys: Move/Rotate, Space: Shoot", True, GREEN)
        screen.blit(ctrl_text, (10, HEIGHT - 40))
    
    # Draw invincibility indicator
    if ship.invincible:
        inv_text = font.render("INVINCIBLE", True, RED)
        screen.blit(inv_text, (WIDTH//2 - inv_text.get_width()//2, 20))
    
    # Draw game over or win message
    if game_over:
        game_over_text = font.render("GAME OVER", True, RED)
        restart_text = font.render("Press R to Restart", True, WHITE)
        screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2 - 50))
        screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 10))
        
    if game_won:
        win_text = font.render("YOU WIN!", True, GREEN)
        restart_text = font.render("Press R to Play Again", True, WHITE)
        screen.blit(win_text, (WIDTH//2 - win_text.get_width()//2, HEIGHT//2 - 50))
        screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 10))

# Main game loop
running = True
while running:
    # Keep loop running at the right speed
    clock.tick(FPS)
    
    # Process input (events)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            if (game_over or game_won) and event.key == pygame.K_r:
                # Reset game
                game_over = False
                game_won = False
                score = 0
                lives = 3
                level = 1
                ship = Ship()
                bullets = []
                asteroids = []
                spawn_asteroids(8)
    
    if not game_over and not game_won:
        # Update
        ship.update()
        
        # Update bullets
        bullets = [bullet for bullet in bullets if bullet.update()]
        
        # Update asteroids
        for asteroid in asteroids:
            asteroid.update()
        
        # Check if bullets hit asteroids
        for bullet in bullets[:]:
            for asteroid in asteroids[:]:
                distance = math.sqrt((bullet.x - asteroid.x)**2 + (bullet.y - asteroid.y)**2)
                if distance < asteroid.radius:
                    bullets.remove(bullet)
                    asteroids.remove(asteroid)
                    new_asteroids = asteroid.break_apart()
                    asteroids.extend(new_asteroids)
                    score += asteroid.points
                    break
        
        # Check if asteroids hit the ship (only if not invincible)
        if not ship.invincible:
            for asteroid in asteroids[:]:
                distance = math.sqrt((ship.x - asteroid.x)**2 + (ship.y - asteroid.y)**2)
                if distance < asteroid.radius + 15:  # 15 is approximate ship size
                    asteroids.remove(asteroid)
                    new_asteroids = asteroid.break_apart()
                    asteroids.extend(new_asteroids)
                    lives -= 1
                    if lives > 0:
                        ship.respawn()
                    else:
                        game_over = True
                    break
                    
        # Check if all asteroids are destroyed
        if len(asteroids) == 0:
            level += 1
            spawn_asteroids(4 + level)
            
        # Win condition
        if score >= 2000:
            game_won = True
    
    # Draw
    draw_background()
    
    # Draw ship
    ship.draw(screen)
    
    # Draw bullets
    for bullet in bullets:
        bullet.draw(screen)
        
    # Draw asteroids
    for asteroid in asteroids:
        asteroid.draw(screen)
    
    # Draw UI
    draw_ui()
    
    # Flip the display
    pygame.display.flip()

pygame.quit()