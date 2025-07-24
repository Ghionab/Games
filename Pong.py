import pygame
import sys
import random

# Initialize pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Two-Player Pong")

# Colors
BACKGROUND = (10, 20, 30)
PADDLE_COLOR = (70, 200, 255)
BALL_COLOR = (255, 255, 200)
NET_COLOR = (100, 100, 150, 150)
TEXT_COLOR = (220, 220, 255)
SCORE_COLOR = (255, 100, 100)
PLAYER1_COLOR = (70, 200, 255)
PLAYER2_COLOR = (255, 100, 100)

# Game objects
PADDLE_WIDTH, PADDLE_HEIGHT = 15, 120
BALL_SIZE = 15
PADDLE_SPEED = 7
BALL_SPEED_X = 5
BALL_SPEED_Y = 5

# Font
font = pygame.font.SysFont(None, 74)
small_font = pygame.font.SysFont(None, 36)

class Paddle:
    def __init__(self, x, y, width, height, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.speed = PADDLE_SPEED
        self.score = 0
    
    def move(self, direction):
        if direction == "up":
            self.rect.y -= self.speed
        elif direction == "down":
            self.rect.y += self.speed
            
        # Keep paddle on screen
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT
    
    def draw(self):
        pygame.draw.rect(screen, self.color, self.rect)
        pygame.draw.rect(screen, (255, 255, 255), self.rect, 2)  # Border

class Ball:
    def __init__(self, x, y, size):
        self.rect = pygame.Rect(x, y, size, size)
        self.size = size
        self.color = BALL_COLOR
        self.reset()
    
    def reset(self):
        self.rect.center = (WIDTH // 2, HEIGHT // 2)
        self.dx = BALL_SPEED_X * random.choice([-1, 1])
        self.dy = BALL_SPEED_Y * random.choice([-1, 1])
    
    def move(self):
        self.rect.x += self.dx
        self.rect.y += self.dy
        
        # Bounce off top and bottom walls
        if self.rect.top <= 0 or self.rect.bottom >= HEIGHT:
            self.dy *= -1
    
    def draw(self):
        pygame.draw.ellipse(screen, self.color, self.rect)
        pygame.draw.ellipse(screen, (255, 255, 255), self.rect, 2)  # Border

def draw_net():
    for y in range(0, HEIGHT, 20):
        pygame.draw.rect(screen, NET_COLOR, (WIDTH // 2 - 2, y, 4, 10))

def draw_scores(player1, player2):
    # Player 1 score (left)
    p1_score = font.render(str(player1.score), True, PLAYER1_COLOR)
    screen.blit(p1_score, (WIDTH // 4, 20))
    
    # Player 2 score (right)
    p2_score = font.render(str(player2.score), True, PLAYER2_COLOR)
    screen.blit(p2_score, (3 * WIDTH // 4 - p2_score.get_width(), 20))
    
    # Player labels
    p1_label = small_font.render("Player 1", True, PLAYER1_COLOR)
    screen.blit(p1_label, (WIDTH // 4 - p1_label.get_width() // 2, 80))
    
    p2_label = small_font.render("Player 2", True, PLAYER2_COLOR)
    screen.blit(p2_label, (3 * WIDTH // 4 - p2_label.get_width() // 2, 80))

def draw_instructions():
    instructions = [
        "Player 1: W/S keys",
        "Player 2: UP/DOWN arrows",
        "First to 5 points wins!",
        "Press R to reset"
    ]
    
    for i, text in enumerate(instructions):
        rendered = small_font.render(text, True, (180, 180, 200))
        screen.blit(rendered, (WIDTH // 2 - rendered.get_width() // 2, HEIGHT - 120 + i * 30))

def draw_game_over(winner):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    screen.blit(overlay, (0, 0))
    
    game_over_text = font.render("GAME OVER", True, TEXT_COLOR)
    winner_text = font.render(f"{winner} Wins!", True, 
                              PLAYER1_COLOR if winner == "Player 1" else PLAYER2_COLOR)
    restart_text = small_font.render("Press R to Restart", True, TEXT_COLOR)
    
    screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 60))
    screen.blit(winner_text, (WIDTH // 2 - winner_text.get_width() // 2, HEIGHT // 2))
    screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 60))

def main():
    # Create game objects
    player1 = Paddle(30, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT, PADDLE_COLOR)
    player2 = Paddle(WIDTH - 30 - PADDLE_WIDTH, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT, PADDLE_COLOR)
    ball = Ball(WIDTH // 2, HEIGHT // 2, BALL_SIZE)
    
    clock = pygame.time.Clock()
    game_over = False
    winner = ""
    
    # Main game loop
    while True:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    # Reset game
                    player1.score = 0
                    player2.score = 0
                    ball.reset()
                    game_over = False
                    winner = ""
        
        if not game_over:
            # Player controls
            keys = pygame.key.get_pressed()
            if keys[pygame.K_w]:
                player1.move("up")
            if keys[pygame.K_s]:
                player1.move("down")
            if keys[pygame.K_UP]:
                player2.move("up")
            if keys[pygame.K_DOWN]:
                player2.move("down")
            
            # Move the ball
            ball.move()
            
            # Ball collision with paddles
            if ball.rect.colliderect(player1.rect) and ball.dx < 0:
                ball.dx *= -1.1  # Increase speed slightly and reverse direction
                # Add vertical angle based on where ball hits paddle
                relative_y = (player1.rect.centery - ball.rect.centery) / (PADDLE_HEIGHT / 2)
                ball.dy = -relative_y * BALL_SPEED_Y
            
            if ball.rect.colliderect(player2.rect) and ball.dx > 0:
                ball.dx *= -1.1  # Increase speed slightly and reverse direction
                # Add vertical angle based on where ball hits paddle
                relative_y = (player2.rect.centery - ball.rect.centery) / (PADDLE_HEIGHT / 2)
                ball.dy = -relative_y * BALL_SPEED_Y
            
            # Scoring
            if ball.rect.left <= 0:
                player2.score += 1
                ball.reset()
                if player2.score >= 5:
                    game_over = True
                    winner = "Player 2"
            
            if ball.rect.right >= WIDTH:
                player1.score += 1
                ball.reset()
                if player1.score >= 5:
                    game_over = True
                    winner = "Player 1"
        
        # Drawing
        screen.fill(BACKGROUND)
        
        # Draw net
        draw_net()
        
        # Draw paddles and ball
        player1.draw()
        player2.draw()
        ball.draw()
        
        # Draw scores
        draw_scores(player1, player2)
        
        # Draw instructions
        draw_instructions()
        
        # Draw game over screen if needed
        if game_over:
            draw_game_over(winner)
        
        # Update display
        pygame.display.flip()
        
        # Cap the frame rate
        clock.tick(60)

if __name__ == "__main__":
    main()