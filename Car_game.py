import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 500, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Car Racing Game")

# Clock
clock = pygame.time.Clock()
FPS = 60

# Colors
WHITE = (255, 255, 255)
GRAY = (100, 100, 100)
YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)
RED = (200, 0, 0)

# Road lines
LINE_WIDTH = 10
LINE_HEIGHT = 50
LINE_GAP = 20

# Load car images
player_car_img = pygame.Surface((50, 100), pygame.SRCALPHA)
pygame.draw.rect(player_car_img, RED, (0, 0, 50, 100), border_radius=8)

enemy_car_img = pygame.Surface((50, 100), pygame.SRCALPHA)
pygame.draw.rect(enemy_car_img, (0, 0, 255), (0, 0, 50, 100), border_radius=8)

# Player class
class PlayerCar:
    def __init__(self):
        self.image = player_car_img
        self.rect = self.image.get_rect(center=(WIDTH//2, HEIGHT - 120))
        self.speed = 5

    def move(self, keys):
        if keys[pygame.K_LEFT] and self.rect.left > 100:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH - 100:
            self.rect.x += self.speed

    def draw(self):
        screen.blit(self.image, self.rect)

# Enemy car class
class EnemyCar:
    def __init__(self):
        self.image = enemy_car_img
        self.rect = self.image.get_rect(center=(random.choice([150, 250, 350]), -100))
        self.speed = random.randint(4, 7)

    def move(self):
        self.rect.y += self.speed

    def draw(self):
        screen.blit(self.image, self.rect)

# Function to draw road & lines
def draw_road(offset):
    pygame.draw.rect(screen, GRAY, (100, 0, WIDTH - 200, HEIGHT))
    for y in range(-LINE_HEIGHT, HEIGHT, LINE_HEIGHT + LINE_GAP):
        pygame.draw.rect(screen, YELLOW, (WIDTH//2 - LINE_WIDTH//2, y + offset, LINE_WIDTH, LINE_HEIGHT))

# Game loop
def main():
    player = PlayerCar()
    enemies = []
    spawn_timer = 0
    score = 0
    line_offset = 0
    running = True
    game_over = False

    while running:
        screen.fill(GREEN := (0, 150, 0))
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        keys = pygame.key.get_pressed()

        if not game_over:
            # Move road lines
            line_offset += 5
            if line_offset >= LINE_HEIGHT + LINE_GAP:
                line_offset = 0

            draw_road(line_offset)

            # Move player
            player.move(keys)
            player.draw()

            # Spawn enemies
            spawn_timer += 1
            if spawn_timer > 60:
                enemies.append(EnemyCar())
                spawn_timer = 0

            # Move and draw enemies
            for enemy in enemies[:]:
                enemy.move()
                enemy.draw()
                if enemy.rect.top > HEIGHT:
                    enemies.remove(enemy)
                    score += 1

                # Collision
                if player.rect.colliderect(enemy.rect):
                    game_over = True

            # Draw score
            font = pygame.font.SysFont(None, 36)
            score_text = font.render(f"Score: {score}", True, WHITE)
            screen.blit(score_text, (10, 10))

        else:
            font = pygame.font.SysFont(None, 72)
            text = font.render("GAME OVER", True, WHITE)
            screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 - 50))

            font_small = pygame.font.SysFont(None, 36)
            restart_text = font_small.render("Press R to Restart or Q to Quit", True, WHITE)
            screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 20))

            if keys[pygame.K_r]:
                main()
            elif keys[pygame.K_q]:
                pygame.quit()
                sys.exit()

        pygame.display.flip()
        clock.tick(FPS)

# Run game
if __name__ == "__main__":
    main()
