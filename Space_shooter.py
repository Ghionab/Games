import pygame
import random
import math
import sys

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Shooter")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 50, 50)
GREEN = (50, 255, 100)
BLUE = (50, 150, 255)
YELLOW = (255, 255, 50)
PURPLE = (180, 70, 220)
CYAN = (0, 200, 255)

# Game variables
clock = pygame.time.Clock()
FPS = 60
score = 0
lives = 3
level = 1
game_over = False
game_won = False
font = pygame.font.SysFont(None, 36)
small_font = pygame.font.SysFont(None, 24)

# Create sounds
def create_laser_sound():
    # Generate a simple laser sound
    sample_rate = 22050
    duration = 0.1
    frequency = 800
    frames = int(duration * sample_rate)
    arr = []
    for i in range(frames):
        t = float(i) / sample_rate
        wave = 4096 * math.sin(2 * math.pi * frequency * t)
        arr.append([wave, wave])
    return pygame.sndarray.make_sound(numpy.array(arr, dtype=numpy.int16)) if 'numpy' in sys.modules else None

def create_explosion_sound():
    # Generate a simple explosion sound
    sample_rate = 22050
    duration = 0.3
    frames = int(duration * sample_rate)
    arr = []
    for i in range(frames):
        t = float(i) / sample_rate
        # Create a decaying noise
        decay = math.exp(-t * 5)
        wave = decay * (random.random() * 4096 - 2048)
        arr.append([wave, wave])
    return pygame.sndarray.make_sound(numpy.array(arr, dtype=numpy.int16)) if 'numpy' in sys.modules else None

# Try to create sounds, fallback to None if numpy not available
try:
    import numpy
    laser_sound = create_laser_sound()
    explosion_sound = create_explosion_sound()
except ImportError:
    laser_sound = None
    explosion_sound = None
    print("NumPy not found. Sound effects disabled.")

# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((50, 40), pygame.SRCALPHA)
        # Draw a simple spaceship
        pygame.draw.polygon(self.image, BLUE, [(0, 20), (50, 20), (25, 0)])
        pygame.draw.rect(self.image, CYAN, (10, 20, 30, 20))
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH // 2
        self.rect.bottom = HEIGHT - 20
        self.speed = 5
        self.shoot_delay = 250  # milliseconds
        self.last_shot = pygame.time.get_ticks()
        
    def update(self):
        # Move player
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH:
            self.rect.x += self.speed
        if keys[pygame.K_UP] and self.rect.top > 0:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN] and self.rect.bottom < HEIGHT:
            self.rect.y += self.speed
            
        # Shooting
        if keys[pygame.K_SPACE]:
            self.shoot()
            
    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            bullet = Bullet(self.rect.centerx, self.rect.top, -10, YELLOW)
            all_sprites.add(bullet)
            player_bullets.add(bullet)
            if laser_sound:
                laser_sound.play()

# Enemy class
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.size = random.randint(30, 60)
        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        # Draw different enemy shapes
        enemy_type = random.randint(1, 3)
        if enemy_type == 1:
            pygame.draw.circle(self.image, RED, (self.size//2, self.size//2), self.size//2)
            pygame.draw.circle(self.image, PURPLE, (self.size//2, self.size//2), self.size//3)
        elif enemy_type == 2:
            pygame.draw.polygon(self.image, RED, [
                (self.size//2, 0),
                (self.size, self.size),
                (0, self.size)
            ])
        else:
            pygame.draw.rect(self.image, RED, (0, 0, self.size, self.size))
            pygame.draw.rect(self.image, PURPLE, (self.size//4, self.size//4, self.size//2, self.size//2))
            
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, WIDTH - self.size)
        self.rect.y = random.randint(-100, -40)
        self.speed_y = random.randint(1, 4)
        self.speed_x = random.randint(-2, 2)
        self.shoot_chance = 0.005  # Chance to shoot each frame
        
    def update(self):
        self.rect.y += self.speed_y
        self.rect.x += self.speed_x
        
        # Bounce off edges
        if self.rect.left < 0 or self.rect.right > WIDTH:
            self.speed_x = -self.speed_x
            
        # Remove if off screen
        if self.rect.top > HEIGHT:
            self.kill()
            
        # Random shooting
        if random.random() < self.shoot_chance:
            self.shoot()
            
    def shoot(self):
        bullet = Bullet(self.rect.centerx, self.rect.bottom, 5, RED)
        all_sprites.add(bullet)
        enemy_bullets.add(bullet)
        if laser_sound:
            laser_sound.play()

# Bullet class
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, speed_y, color):
        super().__init__()
        self.image = pygame.Surface((5, 15))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speed_y = speed_y
        
    def update(self):
        self.rect.y += self.speed_y
        # Remove if off screen
        if self.rect.bottom < 0 or self.rect.top > HEIGHT:
            self.kill()

# Explosion class
class Explosion(pygame.sprite.Sprite):
    def __init__(self, center):
        super().__init__()
        self.size = 50
        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.max_frames = 10
        self.update()
        
    def update(self):
        self.image.fill((0, 0, 0, 0))
        radius = int(self.frame * 2)
        pygame.draw.circle(self.image, YELLOW, (self.size//2, self.size//2), radius)
        pygame.draw.circle(self.image, RED, (self.size//2, self.size//2), radius//2)
        
        self.frame += 1
        if self.frame > self.max_frames:
            self.kill()

# Create sprite groups
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
player_bullets = pygame.sprite.Group()
enemy_bullets = pygame.sprite.Group()
explosions = pygame.sprite.Group()

# Create player
player = Player()
all_sprites.add(player)

# Create enemies
def spawn_enemies(count):
    for _ in range(count):
        enemy = Enemy()
        all_sprites.add(enemy)
        enemies.add(enemy)

# Initial enemy spawn
spawn_enemies(8)

# Draw stars in the background
stars = []
for _ in range(100):
    x = random.randint(0, WIDTH)
    y = random.randint(0, HEIGHT)
    size = random.randint(1, 3)
    speed = random.uniform(0.2, 0.8)
    stars.append([x, y, size, speed])

# Draw background
def draw_background():
    screen.fill(BLACK)
    
    # Draw stars
    for star in stars:
        star[1] += star[3]  # Move star down
        if star[1] > HEIGHT:
            star[1] = 0
            star[0] = random.randint(0, WIDTH)
        pygame.draw.circle(screen, WHITE, (int(star[0]), int(star[1])), star[2])

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
                all_sprites.empty()
                enemies.empty()
                player_bullets.empty()
                enemy_bullets.empty()
                explosions.empty()
                player = Player()
                all_sprites.add(player)
                spawn_enemies(8)
    
    if not game_over and not game_won:
        # Update
        all_sprites.update()
        explosions.update()
        
        # Check if player bullets hit enemies
        hits = pygame.sprite.groupcollide(enemies, player_bullets, True, True)
        for hit in hits:
            score += 10
            explosion = Explosion(hit.rect.center)
            all_sprites.add(explosion)
            explosions.add(explosion)
            if explosion_sound:
                explosion_sound.play()
                
        # Check if enemy bullets hit player
        hits = pygame.sprite.spritecollide(player, enemy_bullets, True)
        for hit in hits:
            lives -= 1
            explosion = Explosion(player.rect.center)
            all_sprites.add(explosion)
            explosions.add(explosion)
            if explosion_sound:
                explosion_sound.play()
            if lives <= 0:
                game_over = True
                
        # Check if enemies hit player
        hits = pygame.sprite.spritecollide(player, enemies, True)
        for hit in hits:
            lives -= 1
            explosion = Explosion(player.rect.center)
            all_sprites.add(explosion)
            explosions.add(explosion)
            if explosion_sound:
                explosion_sound.play()
            if lives <= 0:
                game_over = True
                
        # Spawn new enemies
        if len(enemies) < 5 + level:
            spawn_enemies(1)
            
        # Level up
        if score >= level * 100:
            level += 1
            # Add more enemies for higher levels
            spawn_enemies(level)
            
        # Win condition
        if score >= 1000:
            game_won = True
    
    # Draw
    draw_background()
    all_sprites.draw(screen)
    explosions.draw(screen)
    
    # Draw UI
    score_text = font.render(f"Score: {score}", True, WHITE)
    lives_text = font.render(f"Lives: {lives}", True, WHITE)
    level_text = font.render(f"Level: {level}", True, WHITE)
    screen.blit(score_text, (10, 10))
    screen.blit(lives_text, (10, 50))
    screen.blit(level_text, (10, 90))
    
    # Draw instructions
    if not game_over and not game_won:
        controls = [
            "CONTROLS:",
            "Arrow Keys - Move",
            "Space - Shoot",
            "ESC - Quit"
        ]
        for i, text in enumerate(controls):
            ctrl_text = small_font.render(text, True, GREEN)
            screen.blit(ctrl_text, (WIDTH - 150, 10 + i*25))
    
    # Game over screen
    if game_over:
        game_over_text = font.render("GAME OVER", True, RED)
        restart_text = font.render("Press R to Restart", True, WHITE)
        screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2 - 50))
        screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 10))
        
    # Win screen
    if game_won:
        win_text = font.render("YOU WIN!", True, GREEN)
        restart_text = font.render("Press R to Play Again", True, WHITE)
        screen.blit(win_text, (WIDTH//2 - win_text.get_width()//2, HEIGHT//2 - 50))
        screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 10))
    
    # Flip the display
    pygame.display.flip()

pygame.quit()