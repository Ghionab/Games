class CheckersMultiplier:
    def __init__(self):
        self.board = self.create_board()
        self.current_player = 'X'
        self.scores = {'X': 0, 'O': 0}
        self.game_over = False
        self.winner = None

    def create_board(self):
        # Initialize 8x8 board
        board = [[' ' for _ in range(8)] for _ in range(8)]
        
        # Place pieces for player X (top 3 rows)
        for row in range(3):
            for col in range(8):
                if (row + col) % 2 == 1:
                    board[row][col] = 'x'
        
        # Place pieces for player O (bottom 3 rows)
        for row in range(5, 8):
            for col in range(8):
                if (row + col) % 2 == 1:
                    board[row][col] = 'o'
        
        return board

    def print_board(self):
        print("\n  0 1 2 3 4 5 6 7")
        for i, row in enumerate(self.board):
            print(i, ' '.join('|' + cell for cell in row) + '|')
        print(f"Scores - X: {self.scores['X']}, O: {self.scores['O']}")
        print(f"Current Player: {self.current_player}")

    def is_valid_position(self, row, col):
        return 0 <= row < 8 and 0 <= col < 8

    def get_piece_at(self, row, col):
        if not self.is_valid_position(row, col):
            return None
        return self.board[row][col]

    def is_king(self, piece):
        return piece in ['X', 'O']

    def get_possible_moves(self, row, col):
        piece = self.get_piece_at(row, col)
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
            if self.is_valid_position(new_row, new_col) and self.board[new_row][new_col] == ' ':
                moves.append((new_row, new_col, []))
            
            # Capture move
            new_row, new_col = row + 2*dr, col + 2*dc
            mid_row, mid_col = row + dr, col + dc
            if (self.is_valid_position(new_row, new_col) and 
                self.board[new_row][new_col] == ' ' and
                self.board[mid_row][mid_col] != ' ' and
                self.board[mid_row][mid_col].upper() != player):
                moves.append((new_row, new_col, [(mid_row, mid_col)]))
        
        return moves

    def get_all_possible_moves(self, player):
        moves = []
        capture_moves = []
        
        for row in range(8):
            for col in range(8):
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
            multiplier = len(captures)
            self.scores[self.current_player] += multiplier * 10

    def switch_player(self):
        self.current_player = 'O' if self.current_player == 'X' else 'X'

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

    def play(self):
        print("Welcome to Checkers Multiplier!")
        print("Capture multiple pieces in one turn for score multipliers!")
        print("Format: start_row,start_col,end_row,end_col (e.g., 2,1,3,2)")
        
        while not self.game_over:
            self.print_board()
            moves = self.get_all_possible_moves(self.current_player)
            
            if not moves:
                print(f"No valid moves for {self.current_player}. Game over!")
                self.game_over = True
                self.winner = 'O' if self.current_player == 'X' else 'X'
                break
            
            print(f"Player {self.current_player}'s turn")
            try:
                move_input = input("Enter move (row,col,row,col) or 'quit': ")
                if move_input.lower() == 'quit':
                    print("Game quit by user.")
                    return
                
                coords = list(map(int, move_input.split(',')))
                if len(coords) != 4:
                    print("Invalid input. Please enter 4 numbers.")
                    continue
                    
                start_row, start_col, end_row, end_col = coords
                
                # Validate move
                selected_move = None
                for move in moves:
                    if (move[0] == start_row and move[1] == start_col and 
                        move[2] == end_row and move[3] == end_col):
                        selected_move = move
                        break
                
                if selected_move:
                    self.make_move(*selected_move)
                    
                    # Chain captures if available
                    if selected_move[4]:  # If it was a capture
                        chain_moves = self.get_possible_moves(end_row, end_col)
                        chain_captures = [move for move in chain_moves if move[2]]
                        if chain_captures:
                            print("Chain capture available! You get another turn.")
                            continue  # Don't switch player
                    
                    self.switch_player()
                else:
                    print("Invalid move. Try again.")
                    continue
                    
            except (ValueError, IndexError):
                print("Invalid input. Please use format: row,col,row,col")
                continue
            
            self.check_game_over()
        
        self.print_board()
        if self.winner:
            print(f"Game Over! Player {self.winner} wins!")
        else:
            print("Game ended in a draw!")

if __name__ == "__main__":
    game = CheckersMultiplier()
    game.play()