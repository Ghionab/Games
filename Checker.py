import pygame
import sys

# ---------- CONSTANTS ----------
WIDTH, HEIGHT = 800, 800
ROWS, COLS = 8, 8
SQ = WIDTH // COLS

RED     = (25,   0,   0)
WHITE   = (255, 255, 255)
BLACK   = (  100,  100,   0)
GREY    = (128, 128, 128)
BLUE    = (  0,   0, 255)

pygame.init()
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pygame Checkers")
FPS = 60

# ---------- PIECE ----------
class Piece:
    PADDING = 15
    OUTLINE = 2

    def __init__(self, row, col, color):
        self.row = row
        self.col = col
        self.color = color
        self.king  = False
        self.calc_pos()

    def calc_pos(self):
        self.x = SQ * self.col + SQ // 2
        self.y = SQ * self.row + SQ // 2

    def make_king(self):
        self.king = True

    def draw(self, win):
        radius = SQ // 2 - self.PADDING
        pygame.draw.circle(win, BLACK, (self.x, self.y), radius + self.OUTLINE)
        pygame.draw.circle(win, self.color, (self.x, self.y), radius)
        if self.king:
            pygame.draw.circle(win, (255, 215, 0), (self.x, self.y), radius // 2)

    def move(self, row, col):
        self.row, self.col = row, col
        self.calc_pos()

# ---------- BOARD ----------
class Board:
    def __init__(self):
        self.board = []
        self.selected = None
        self.red_left = self.white_left = 12
        self.red_kings = self.white_kings = 0
        self.create_board()

    # ---------- DRAW ----------
    def draw_squares(self, win):
        win.fill(BLACK)
        for r in range(ROWS):
            for c in range(r % 2, COLS, 2):
                pygame.draw.rect(win, RED, (r*SQ, c*SQ, SQ, SQ))

    def create_board(self):
        for r in range(ROWS):
            self.board.append([])
            for c in range(COLS):
                if c % 2 == ((r + 1) % 2):
                    if r < 3:
                        self.board[r].append(Piece(r, c, WHITE))
                    elif r > 4:
                        self.board[r].append(Piece(r, c, BLACK))
                    else:
                        self.board[r].append(0)
                else:
                    self.board[r].append(0)

    def draw(self, win):
        self.draw_squares(win)
        for r in range(ROWS):
            for c in range(COLS):
                piece = self.board[r][c]
                if piece != 0:
                    piece.draw(win)

    # ---------- MOVE HELPERS ----------
    def get_piece(self, r, c):
        return self.board[r][c]

    def move(self, piece, r, c):
        self.board[piece.row][piece.col], self.board[r][c] = self.board[r][c], self.board[piece.row][piece.col]
        piece.move(r, c)
        if (r == ROWS - 1 or r == 0) and not piece.king:
            piece.make_king()
            if piece.color == WHITE:
                self.white_kings += 1
            else:
                self.red_kings += 1

    def remove(self, pieces):
        for piece in pieces:
            self.board[piece.row][piece.col] = 0
            if piece != 0:
                if piece.color == BLACK:
                    self.red_left -= 1
                else:
                    self.white_left -= 1

    def get_valid_moves(self, piece):
        moves = {}
        left  = piece.col - 1
        right = piece.col + 1
        row   = piece.row
        if piece.color == BLACK or piece.king:
            moves.update(self._traverse_left(row - 1, max(row - 3, -1), -1, piece.color, left))
            moves.update(self._traverse_right(row - 1, max(row - 3, -1), -1, piece.color, right))
        if piece.color == WHITE or piece.king:
            moves.update(self._traverse_left(row + 1, min(row + 3, ROWS), 1, piece.color, left))
            moves.update(self._traverse_right(row + 1, min(row + 3, ROWS), 1, piece.color, right))
        return moves

    def _traverse_left(self, start, stop, step, color, left, skipped=[]):
        moves = {}; last = []
        for r in range(start, stop, step):
            if left < 0: break
            current = self.board[r][left]
            if current == 0:
                if skipped and not last:
                    break
                elif skipped:
                    moves[(r, left)] = last + skipped
                else:
                    moves[(r, left)] = last
                if last:
                    row = max(r-3, 0) if step == -1 else min(r+3, ROWS)
                    moves.update(self._traverse_left(r+step, row, step, color, left-1, skipped=last))
                    moves.update(self._traverse_right(r+step, row, step, color, left+1, skipped=last))
                break
            elif current.color == color:
                break
            else:
                last = [current]
            left -= 1
        return moves

    def _traverse_right(self, start, stop, step, color, right, skipped=[]):
        moves = {}; last = []
        for r in range(start, stop, step):
            if right >= COLS: break
            current = self.board[r][right]
            if current == 0:
                if skipped and not last:
                    break
                elif skipped:
                    moves[(r, right)] = last + skipped
                else:
                    moves[(r, right)] = last
                if last:
                    row = max(r-3, 0) if step == -1 else min(r+3, ROWS)
                    moves.update(self._traverse_left(r+step, row, step, color, right-1, skipped=last))
                    moves.update(self._traverse_right(r+step, row, step, color, right+1, skipped=last))
                break
            elif current.color == color:
                break
            else:
                last = [current]
            right += 1
        return moves

# ---------- GAME ----------
class Game:
    def __init__(self, win):
        self._init()
        self.win = win

    def _init(self):
        self.selected = None
        self.board = Board()
        self.turn = BLACK
        self.valid_moves = {}

    def update(self):
        self.board.draw(self.win)
        self.draw_valid_moves(self.valid_moves)
        pygame.display.update()

    def reset(self):
        self._init()

    def select(self, row, col):
        if self.selected:
            result = self._move(row, col)
            if not result:
                self.selected = None
                self.select(row, col)
        piece = self.board.get_piece(row, col)
        if piece != 0 and piece.color == self.turn:
            self.selected = piece
            self.valid_moves = self.board.get_valid_moves(piece)
            return True
        return False

    def _move(self, row, col):
        piece = self.board.get_piece(row, col)
        if self.selected and piece == 0 and (row, col) in self.valid_moves:
            self.board.move(self.selected, row, col)
            skipped = self.valid_moves[(row, col)]
            if skipped:
                self.board.remove(skipped)
            self.change_turn()
        else:
            return False
        return True

    def draw_valid_moves(self, moves):
        for move in moves:
            row, col = move
            pygame.draw.circle(self.win, BLUE, (col*SQ + SQ//2, row*SQ + SQ//2), 15)

    def change_turn(self):
        self.valid_moves = {}
        self.turn = WHITE if self.turn == BLACK else BLACK

    def winner(self):
        if self.board.red_left <= 0:
            return "White Wins!"
        elif self.board.white_left <= 0:
            return "Black Wins!"
        return None

# ---------- UTIL ----------
def get_row_col_from_mouse(pos):
    x, y = pos
    return y // SQ, x // SQ

# ---------- MAIN ----------
def main():
    clock = pygame.time.Clock()
    game = Game(WIN)
    run = True
    while run:
        clock.tick(FPS)
        if game.winner():
            print(game.winner())
            run = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                row, col = get_row_col_from_mouse(pos)
                game.select(row, col)
        game.update()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()