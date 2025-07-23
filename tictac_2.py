import pygame
import sys

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 600, 700
BOARD_SIZE = 450
GRID_SIZE = BOARD_SIZE // 3
LINE_WIDTH = 15
CIRCLE_WIDTH = 15
CROSS_WIDTH = 20
CIRCLE_RADIUS = GRID_SIZE // 3
SPACE = GRID_SIZE // 4

# Colors
BG_COLOR = (28, 170, 156)
LINE_COLOR = (23, 145, 135)
CIRCLE_COLOR = (239, 231, 200)
CROSS_COLOR = (66, 66, 66)
TEXT_COLOR = (255, 255, 255)
BUTTON_COLOR = (70, 130, 180)
BUTTON_HOVER_COLOR = (100, 149, 237)

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Tic Tac Toe')
screen.fill(BG_COLOR)

# Game variables
board = [[None for _ in range(3)] for _ in range(3)]
player = 'X'
game_over = False
winner = None

# Fonts
font = pygame.font.SysFont('Arial', 40)
small_font = pygame.font.SysFont('Arial', 30)

def draw_lines():
    # Horizontal lines
    pygame.draw.line(screen, LINE_COLOR, (75, 75 + GRID_SIZE), (75 + BOARD_SIZE, 75 + GRID_SIZE), LINE_WIDTH)
    pygame.draw.line(screen, LINE_COLOR, (75, 75 + 2 * GRID_SIZE), (75 + BOARD_SIZE, 75 + 2 * GRID_SIZE), LINE_WIDTH)
    
    # Vertical lines
    pygame.draw.line(screen, LINE_COLOR, (75 + GRID_SIZE, 75), (75 + GRID_SIZE, 75 + BOARD_SIZE), LINE_WIDTH)
    pygame.draw.line(screen, LINE_COLOR, (75 + 2 * GRID_SIZE, 75), (75 + 2 * GRID_SIZE, 75 + BOARD_SIZE), LINE_WIDTH)

def draw_figures():
    for row in range(3):
        for col in range(3):
            if board[row][col] == 'O':
                pygame.draw.circle(screen, CIRCLE_COLOR, 
                                  (col * GRID_SIZE + 75 + GRID_SIZE // 2, row * GRID_SIZE + 75 + GRID_SIZE // 2), 
                                  CIRCLE_RADIUS, CIRCLE_WIDTH)
            elif board[row][col] == 'X':
                # Draw X
                pygame.draw.line(screen, CROSS_COLOR, 
                                (col * GRID_SIZE + 75 + SPACE, row * GRID_SIZE + 75 + SPACE),
                                (col * GRID_SIZE + 75 + GRID_SIZE - SPACE, row * GRID_SIZE + 75 + GRID_SIZE - SPACE), 
                                CROSS_WIDTH)
                pygame.draw.line(screen, CROSS_COLOR, 
                                (col * GRID_SIZE + 75 + SPACE, row * GRID_SIZE + 75 + GRID_SIZE - SPACE),
                                (col * GRID_SIZE + 75 + GRID_SIZE - SPACE, row * GRID_SIZE + 75 + SPACE), 
                                CROSS_WIDTH)

def mark_square(row, col, player):
    board[row][col] = player

def available_square(row, col):
    return board[row][col] is None

def is_board_full():
    for row in range(3):
        for col in range(3):
            if board[row][col] is None:
                return False
    return True

def check_win(player):
    # Vertical win check
    for col in range(3):
        if board[0][col] == player and board[1][col] == player and board[2][col] == player:
            draw_vertical_winning_line(col, player)
            return True

    # Horizontal win check
    for row in range(3):
        if board[row][0] == player and board[row][1] == player and board[row][2] == player:
            draw_horizontal_winning_line(row, player)
            return True

    # Ascending diagonal win check
    if board[2][0] == player and board[1][1] == player and board[0][2] == player:
        draw_asc_diagonal(player)
        return True

    # Descending diagonal win check
    if board[0][0] == player and board[1][1] == player and board[2][2] == player:
        draw_desc_diagonal(player)
        return True

    return False

def draw_vertical_winning_line(col, player):
    posX = col * GRID_SIZE + 75 + GRID_SIZE // 2
    
    color = CIRCLE_COLOR if player == 'O' else CROSS_COLOR
    pygame.draw.line(screen, color, (posX, 95), (posX, 75 + BOARD_SIZE - 15), 15)

def draw_horizontal_winning_line(row, player):
    posY = row * GRID_SIZE + 75 + GRID_SIZE // 2
    
    color = CIRCLE_COLOR if player == 'O' else CROSS_COLOR
    pygame.draw.line(screen, color, (95, posY), (75 + BOARD_SIZE - 15, posY), 15)

def draw_asc_diagonal(player):
    color = CIRCLE_COLOR if player == 'O' else CROSS_COLOR
    pygame.draw.line(screen, color, (110, 75 + BOARD_SIZE - 15), (75 + BOARD_SIZE - 15, 95), 15)

def draw_desc_diagonal(player):
    color = CIRCLE_COLOR if player == 'O' else CROSS_COLOR
    pygame.draw.line(screen, color, (110, 95), (75 + BOARD_SIZE - 15, 75 + BOARD_SIZE - 15), 15)

def restart():
    screen.fill(BG_COLOR)
    draw_lines()
    for row in range(3):
        for col in range(3):
            board[row][col] = None

def draw_status():
    # Draw current player indicator
    if not game_over:
        text = font.render(f"Player {player}'s Turn", True, TEXT_COLOR)
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 20))
    else:
        if winner:
            text = font.render(f"Player {winner} Wins!", True, TEXT_COLOR)
        else:
            text = font.render("Game Over: Draw!", True, TEXT_COLOR)
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 20))

def draw_restart_button():
    button_rect = pygame.Rect(WIDTH // 2 - 75, HEIGHT - 70, 150, 50)
    mouse_pos = pygame.mouse.get_pos()
    
    # Change color if mouse is hovering over button
    if button_rect.collidepoint(mouse_pos):
        pygame.draw.rect(screen, BUTTON_HOVER_COLOR, button_rect, border_radius=10)
    else:
        pygame.draw.rect(screen, BUTTON_COLOR, button_rect, border_radius=10)
    
    pygame.draw.rect(screen, (255, 255, 255), button_rect, 2, border_radius=10)
    
    text = small_font.render("RESTART", True, TEXT_COLOR)
    screen.blit(text, (button_rect.centerx - text.get_width() // 2, 
                      button_rect.centery - text.get_height() // 2))
    
    return button_rect

# Draw initial board
draw_lines()

# Main game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        
        if event.type == pygame.MOUSEBUTTONDOWN and not game_over:
            mouseX = event.pos[0]  # x coordinate
            mouseY = event.pos[1]  # y coordinate
            
            # Check if click is within the board area
            if 75 <= mouseX <= 75 + BOARD_SIZE and 75 <= mouseY <= 75 + BOARD_SIZE:
                clicked_row = (mouseY - 75) // GRID_SIZE
                clicked_col = (mouseX - 75) // GRID_SIZE
                
                if available_square(clicked_row, clicked_col):
                    mark_square(clicked_row, clicked_col, player)
                    if check_win(player):
                        game_over = True
                        winner = player
                    elif is_board_full():
                        game_over = True
                        winner = None
                    else:
                        player = 'O' if player == 'X' else 'X'
                    
                    draw_figures()
        
        # Handle restart button click
        if event.type == pygame.MOUSEBUTTONDOWN and game_over:
            button_rect = draw_restart_button()
            if button_rect.collidepoint(event.pos):
                restart()
                game_over = False
                player = 'X'
                winner = None
    
    # Update display
    draw_status()
    draw_figures()
    button_rect = draw_restart_button()
    pygame.display.update()