import pygame
import sys

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
BOARD_SIZE = 8
SQUARE_SIZE = 60
BOARD_PADDING = 50
PIECE_RADIUS = SQUARE_SIZE // 2 - 5

# Colors
DARK_BROWN = (101, 67, 33)
LIGHT_BROWN = (222, 184, 135)
RED = (220, 20, 60)
BLUE = (30, 144, 255)
YELLOW = (255, 215, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (50, 205, 50)
HIGHLIGHT = (255, 255, 0, 128)  # Semi-transparent yellow

# Set up display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Checkers Multiplier")

# Fonts
font = pygame.font.SysFont(None, 36)
small_font = pygame.font.SysFont(None, 28)

class CheckersGame:
    def __init__(self):
        self.board = self.create_board()
        self.current_player = 'X'
        self.scores = {'X': 0, 'O': 0}
        self.selected_piece = None
        self.valid_moves = []
        self.game_over = False
        self.winner = None
        self.message = ""
        self.multiplier = 1

    def create_board(self):
        board = [[' ' for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        
        # Place pieces for player X (top 3 rows)
        for row in range(3):
            for col in range(BOARD_SIZE):
                if (row + col) % 2 == 1:
                    board[row][col] = 'x'
        
        # Place pieces for player O (bottom 3 rows)
        for row in range(5, 8):
            for col in range(BOARD_SIZE):
                if (row + col) % 2 == 1:
                    board[row][col] = 'o'
        
        return board

    def draw_board(self):
        # Draw board background
        screen.fill(DARK_BROWN)
        
        # Draw squares
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                color = LIGHT_BROWN if (row + col) % 2 == 0 else DARK_BROWN
                pygame.draw.rect(screen, color, (
                    BOARD_PADDING + col * SQUARE_SIZE,
                    BOARD_PADDING + row * SQUARE_SIZE,
                    SQUARE_SIZE, SQUARE_SIZE
                ))
        
        # Highlight selected piece
        if self.selected_piece:
            row, col = self.selected_piece
            pygame.draw.rect(screen, YELLOW, (
                BOARD_PADDING + col * SQUARE_SIZE,
                BOARD_PADDING + row * SQUARE_SIZE,
                SQUARE_SIZE, SQUARE_SIZE
            ), 3)
        
        # Highlight valid moves
        for move in self.valid_moves:
            row, col = move[0], move[1]
            pygame.draw.circle(screen, GREEN, (
                BOARD_PADDING + col * SQUARE_SIZE + SQUARE_SIZE // 2,
                BOARD_PADDING + row * SQUARE_SIZE + SQUARE_SIZE // 2
            ), 10)
        
        # Draw pieces
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                piece = self.board[row][col]
                if piece != ' ':
                    color = RED if piece.lower() == 'x' else BLUE
                    center_x = BOARD_PADDING + col * SQUARE_SIZE + SQUARE_SIZE // 2
                    center_y = BOARD_PADDING + row * SQUARE_SIZE + SQUARE_SIZE // 2
                    pygame.draw.circle(screen, color, (center_x, center_y), PIECE_RADIUS)
                    
                    # Draw king symbol
                    if piece.isupper():
                        pygame.draw.circle(screen, YELLOW, (center_x, center_y), PIECE_RADIUS // 2)

    def draw_ui(self):
        # Draw scores
        score_text = font.render(f"X: {self.scores['X']}    O: {self.scores['O']}", True, WHITE)
        screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 20))
        
        # Draw current player
        player_text = font.render(f"Current Player: {self.current_player}", True, WHITE)
        screen.blit(player_text, (WIDTH // 2 - player_text.get_width() // 2, HEIGHT - 60))
        
        # Draw message
        if self.message:
            msg_text = small_font.render(self.message, True, YELLOW)
            screen.blit(msg_text, (WIDTH // 2 - msg_text.get_width() // 2, HEIGHT - 30))
        
        # Draw multiplier
        if self.multiplier > 1:
            mult_text = font.render(f"Multiplier: {self.multiplier}x", True, YELLOW)
            screen.blit(mult_text, (WIDTH - mult_text.get_width() - 20, 20))

    def get_board_position(self, pos):
        x, y = pos
        col = (x - BOARD_PADDING) // SQUARE_SIZE
        row = (y - BOARD_PADDING) // SQUARE_SIZE
        if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE:
            return (row, col)
        return None

    def is_king(self, piece):
        return piece in ['X', 'O']

    def get_possible_moves(self, row, col):
        piece = self.board[row][col]
        if not piece or piece == ' ':
            return []
        
        moves = []
        is_king = self.is_king(piece)
        player = piece.upper()
        
        # Determine movement directions based on piece type
        directions = []
        if player == 'X' or is_king:
            directions.extend([(1, -1), (1, 1)])  # Down-left, Down-right
        if player == 'O' or is_king:
            directions.extend([(-1, -1), (-1, 1)])  # Up-left, Up-right
            
        # Check regular moves and captures
        for dr, dc in directions:
            # Regular move
            new_row, new_col = row + dr, col + dc
            if (0 <= new_row < BOARD_SIZE and 0 <= new_col < BOARD_SIZE and 
                self.board[new_row][new_col] == ' '):
                moves.append((new_row, new_col, []))
            
            # Capture move
            new_row, new_col = row + 2*dr, col + 2*dc
            mid_row, mid_col = row + dr, col + dc
            if (0 <= new_row < BOARD_SIZE and 0 <= new_col < BOARD_SIZE and 
                self.board[new_row][new_col] == ' ' and
                self.board[mid_row][mid_col] != ' ' and
                self.board[mid_row][mid_col].upper() != player):
                moves.append((new_row, new_col, [(mid_row, mid_col)]))
        
        return moves

    def get_all_possible_moves(self, player):
        moves = []
        capture_moves = []
        
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                piece = self.board[row][col]
                if piece != ' ' and piece.upper() == player:
                    piece_moves = self.get_possible_moves(row, col)
                    for move in piece_moves:
                        if move[2]:  # If there are captures
                            capture_moves.append((row, col, move[0], move[1], move[2]))
                        else:
                            moves.append((row, col, move[0], move[1], []))
        
        # If any capture moves exist, only return those
        return capture_moves if capture_moves else moves

    def make_move(self, start_row, start_col, end_row, end_col, captures):
        piece = self.board[start_row][start_col]
        self.board[start_row][start_col] = ' '
        
        # Move the piece
        self.board[end_row][end_col] = piece
        
        # Remove captured pieces
        for cap_row, cap_col in captures:
            self.board[cap_row][cap_col] = ' '
        
        # Promote to king if reached the opposite end
        if (piece == 'x' and end_row == 7) or (piece == 'o' and end_row == 0):
            self.board[end_row][end_col] = piece.upper()
        
        # Update score (multiplier based on number of captures)
        if captures:
            self.multiplier = len(captures)
            self.scores[self.current_player] += self.multiplier * 10
            return True  # Indicates a capture was made
        return False

    def switch_player(self):
        self.current_player = 'O' if self.current_player == 'X' else 'X'
        self.multiplier = 1

    def check_game_over(self):
        x_pieces = sum(row.count('x') + row.count('X') for row in self.board)
        o_pieces = sum(row.count('o') + row.count('O') for row in self.board)
        
        if x_pieces == 0:
            self.game_over = True
            self.winner = 'O'
        elif o_pieces == 0:
            self.game_over = True
            self.winner = 'X'
        else:
            moves = self.get_all_possible_moves(self.current_player)
            if not moves:
                self.game_over = True
                self.winner = 'O' if self.current_player == 'X' else 'X'

    def handle_click(self, pos):
        if self.game_over:
            return
            
        board_pos = self.get_board_position(pos)
        if not board_pos:
            return
            
        row, col = board_pos
        piece = self.board[row][col]
        
        # If clicking on a valid move
        if self.selected_piece and (row, col) in [(move[0], move[1]) for move in self.valid_moves]:
            start_row, start_col = self.selected_piece
            captures = []
            
            # Find the move details
            for move in self.valid_moves:
                if move[0] == row and move[1] == col:
                    captures = move[2]
                    break
            
            # Make the move
            capture_made = self.make_move(start_row, start_col, row, col, captures)
            
            # Check for chain captures
            if capture_made:
                chain_moves = self.get_possible_moves(row, col)
                chain_captures = [move for move in chain_moves if move[2]]
                if chain_captures:
                    self.message = "Chain capture! Move again."
                    self.selected_piece = (row, col)
                    self.valid_moves = chain_moves
                    return
            
            # Switch player if no chain capture
            self.switch_player()
            self.selected_piece = None
            self.valid_moves = []
            self.check_game_over()
            
            if self.game_over:
                self.message = f"Game Over! Player {self.winner} wins!"
            else:
                self.message = ""
            return
        
        # If clicking on own piece, select it
        if piece != ' ' and piece.upper() == self.current_player:
            self.selected_piece = (row, col)
            self.valid_moves = self.get_possible_moves(row, col)
            self.message = "Select a destination"
            return
        
        # Deselect if clicking elsewhere
        self.selected_piece = None
        self.valid_moves = []
        self.message = ""

def main():
    game = CheckersGame()
    clock = pygame.time.Clock()
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                game.handle_click(event.pos)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    game = CheckersGame()  # Reset game
        
        # Draw everything
        game.draw_board()
        game.draw_ui()
        
        # Draw game over message
        if game.game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))
            
            win_text = font.render(f"Player {game.winner} Wins!", True, WHITE)
            restart_text = small_font.render("Press 'R' to restart", True, WHITE)
            
            screen.blit(win_text, (WIDTH//2 - win_text.get_width()//2, HEIGHT//2 - 30))
            screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 20))
        
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()