import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Simple Car Game")

# Colors
WHITE = (255, 255, 255)
GRAY = (169, 169, 169)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# Clock
clock = pygame.time.Clock()

# Car setup
car_width = 50
car_height = 100
car_x = WIDTH // 2 - car_width // 2
car_y = HEIGHT - car_height - 10
car_speed = 5

# Obstacle setup
obstacle_width = 50
obstacle_height = 100
obstacle_speed = 7
obstacles = []

# Score
score = 0
font = pygame.font.SysFont(None, 35)

def draw_car(x, y):
    pygame.draw.rect(screen, RED, (x, y, car_width, car_height))

def draw_obstacles(obs_list):
    for obs in obs_list:
        pygame.draw.rect(screen, BLACK, obs)

def display_score(scr):
    score_text = font.render(f"Score: {scr}", True, BLACK)
    screen.blit(score_text, (10, 10))

# Main loop
running = True
while running:
    screen.fill(GRAY)

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Key presses
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and car_x > 0:
        car_x -= car_speed
    if keys[pygame.K_RIGHT] and car_x < WIDTH - car_width:
        car_x += car_speed

    # Spawn obstacles
    if random.randint(1, 20) == 1:
        obs_x = random.randint(0, WIDTH - obstacle_width)
        obs_y = -obstacle_height
        obstacles.append(pygame.Rect(obs_x, obs_y, obstacle_width, obstacle_height))

    # Move obstacles
    for obs in obstacles:
        obs.y += obstacle_speed
        if obs.y > HEIGHT:
            obstacles.remove(obs)
            score += 1

    # Collision detection
    car_rect = pygame.Rect(car_x, car_y, car_width, car_height)
    for obs in obstacles:
        if car_rect.colliderect(obs):
            print("Game Over!")
            pygame.quit()
            sys.exit()

    # Drawing
    draw_car(car_x, car_y)
    draw_obstacles(obstacles)
    display_score(score)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
