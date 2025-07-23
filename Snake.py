import pygame
import sys
import random
import math

# Initialize pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
GRID_SIZE = 20
GRID_WIDTH = WIDTH // GRID_SIZE
GRID_HEIGHT = HEIGHT // GRID_SIZE

# Colors
BACKGROUND = (15, 30, 15)
GRID_COLOR = (30, 60, 30)
SNAKE_HEAD = (50, 205, 50)
SNAKE_BODY = (34, 139, 34)
FOOD_COLOR = (220, 60, 60)
TEXT_COLOR = (200, 220, 200)
BORDER_COLOR = (70, 130, 70)
GAME_OVER_BG = (0, 0, 0, 180)

# Game settings
FPS = 10
INITIAL_LENGTH = 3

# Create the screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Nokia Snake")
clock = pygame.time.Clock()

# Font setup
font_large = pygame.font.SysFont("Arial", 48, bold=True)
font_medium = pygame.font.SysFont("Arial", 32, bold=True)
font_small = pygame.font.SysFont("Arial", 24)

class Snake:
    def __init__(self):
        self.reset()
        
    def reset(self):
        self.length = INITIAL_LENGTH
        self.positions = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)])
        self.score = 0
        self.grow_to = INITIAL_LENGTH
        self.last_move_time = 0
        self.move_delay = 100  # milliseconds
        
    def get_head_position(self):
        return self.positions[0]
    
    def update(self, current_time):
        if current_time - self.last_move_time > self.move_delay:
            self.last_move_time = current_time
            head = self.get_head_position()
            x, y = self.direction
            new_x = (head[0] + x) % GRID_WIDTH
            new_y = (head[1] + y) % GRID_HEIGHT
            new_position = (new_x, new_y)
            
            # Check for collision with self
            if new_position in self.positions[1:]:
                return False
                
            self.positions.insert(0, new_position)
            
            if len(self.positions) > self.grow_to:
                self.positions.pop()
                
        return True
    
    def change_direction(self, direction):
        # Prevent 180-degree turns
        if (direction[0] * -1, direction[1] * -1) != self.direction:
            self.direction = direction
    
    def grow(self):
        self.grow_to += 1
        self.score += 10
    
    def draw(self, surface):
        for i, pos in enumerate(self.positions):
            color = SNAKE_HEAD if i == 0 else SNAKE_BODY
            rect = pygame.Rect(pos[0] * GRID_SIZE, pos[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE)
            pygame.draw.rect(surface, color, rect)
            pygame.draw.rect(surface, (20, 80, 20), rect, 1)
            
            # Draw eyes on the head
            if i == 0:
                # Determine eye positions based on direction
                dx, dy = self.direction
                eye_size = GRID_SIZE // 5
                
                # Left eye
                left_eye_x = pos[0] * GRID_SIZE + GRID_SIZE // 3
                left_eye_y = pos[1] * GRID_SIZE + GRID_SIZE // 3
                
                # Right eye
                right_eye_x = pos[0] * GRID_SIZE + 2 * GRID_SIZE // 3
                right_eye_y = pos[1] * GRID_SIZE + GRID_SIZE // 3
                
                # Adjust for direction
                if dx == 1:  # Moving right
                    left_eye_x += GRID_SIZE // 6
                    right_eye_x += GRID_SIZE // 6
                    left_eye_y -= GRID_SIZE // 6
                    right_eye_y += GRID_SIZE // 6
                elif dx == -1:  # Moving left
                    left_eye_x -= GRID_SIZE // 6
                    right_eye_x -= GRID_SIZE // 6
                    left_eye_y -= GRID_SIZE // 6
                    right_eye_y += GRID_SIZE // 6
                elif dy == 1:  # Moving down
                    left_eye_x -= GRID_SIZE // 6
                    right_eye_x += GRID_SIZE // 6
                    left_eye_y += GRID_SIZE // 6
                    right_eye_y += GRID_SIZE // 6
                elif dy == -1:  # Moving up
                    left_eye_x -= GRID_SIZE // 6
                    right_eye_x += GRID_SIZE // 6
                    left_eye_y -= GRID_SIZE // 6
                    right_eye_y -= GRID_SIZE // 6
                
                pygame.draw.circle(surface, (0, 0, 0), (left_eye_x, left_eye_y), eye_size)
                pygame.draw.circle(surface, (0, 0, 0), (right_eye_x, right_eye_y), eye_size)

class Food:
    def __init__(self):
        self.position = (0, 0)
        self.randomize_position()
        
    def randomize_position(self):
        self.position = (random.randint(0, GRID_WIDTH - 1), 
                         random.randint(0, GRID_HEIGHT - 1))
    
    def draw(self, surface):
        rect = pygame.Rect(self.position[0] * GRID_SIZE, self.position[1] * GRID_SIZE, 
                           GRID_SIZE, GRID_SIZE)
        pygame.draw.rect(surface, FOOD_COLOR, rect)
        pygame.draw.rect(surface, (180, 30, 30), rect, 1)
        
        # Draw a shine effect
        shine_rect = pygame.Rect(self.position[0] * GRID_SIZE + GRID_SIZE//4, 
                                self.position[1] * GRID_SIZE + GRID_SIZE//4, 
                                GRID_SIZE//4, GRID_SIZE//4)
        pygame.draw.ellipse(surface, (255, 200, 200), shine_rect)

def draw_grid(surface):
    for y in range(0, HEIGHT, GRID_SIZE):
        for x in range(0, WIDTH, GRID_SIZE):
            rect = pygame.Rect(x, y, GRID_SIZE, GRID_SIZE)
            pygame.draw.rect(surface, GRID_COLOR, rect, 1)

def draw_score(surface, score):
    score_text = font_medium.render(f"Score: {score}", True, TEXT_COLOR)
    surface.blit(score_text, (20, 20))

def draw_game_over(surface, score):
    # Semi-transparent overlay
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill(GAME_OVER_BG)
    surface.blit(overlay, (0, 0))
    
    # Game over text
    game_over_text = font_large.render("GAME OVER", True, (220, 60, 60))
    score_text = font_medium.render(f"Final Score: {score}", True, TEXT_COLOR)
    restart_text = font_small.render("Press SPACE to play again", True, TEXT_COLOR)
    
    surface.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2 - 60))
    surface.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT//2))
    surface.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 60))

def draw_title(surface):
    title_text = font_large.render("NOKIA SNAKE", True, (100, 200, 100))
    surface.blit(title_text, (WIDTH//2 - title_text.get_width()//2, 20))

def draw_instructions(surface):
    instructions = [
        "CONTROLS:",
        "Arrow Keys - Move Snake",
        "SPACE - Restart Game",
        "ESC - Quit"
    ]
    
    for i, text in enumerate(instructions):
        inst_text = font_small.render(text, True, TEXT_COLOR)
        surface.blit(inst_text, (WIDTH - inst_text.get_width() - 20, 20 + i * 30))

def main():
    snake = Snake()
    food = Food()
    game_over = False
    
    # Main game loop
    while True:
        current_time = pygame.time.get_ticks()
        
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if event.type == pygame.KEYDOWN:
                if game_over and event.key == pygame.K_SPACE:
                    snake.reset()
                    food.randomize_position()
                    game_over = False
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                    
                if not game_over:
                    if event.key == pygame.K_UP:
                        snake.change_direction((0, -1))
                    elif event.key == pygame.K_DOWN:
                        snake.change_direction((0, 1))
                    elif event.key == pygame.K_LEFT:
                        snake.change_direction((-1, 0))
                    elif event.key == pygame.K_RIGHT:
                        snake.change_direction((1, 0))
        
        # Drawing
        screen.fill(BACKGROUND)
        draw_grid(screen)
        draw_title(screen)
        draw_instructions(screen)
        draw_score(screen, snake.score)
        
        if not game_over:
            # Update snake position
            if not snake.update(current_time):
                game_over = True
                
            # Check for food collision
            if snake.get_head_position() == food.position:
                snake.grow()
                food.randomize_position()
                # Make sure food doesn't appear on snake
                while food.position in snake.positions:
                    food.randomize_position()
            
            # Draw game objects
            food.draw(screen)
            snake.draw(screen)
        else:
            draw_game_over(screen, snake.score)
        
        # Draw border
        pygame.draw.rect(screen, BORDER_COLOR, (0, 0, WIDTH, HEIGHT), 4)
        
        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()