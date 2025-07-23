def print_board(board):
    """Display the Tic Tac Toe board."""
    print("\n")
    for i in range(3):
        print(f" {board[i][0]} | {board[i][1]} | {board[i][2]} ")
        if i < 2:
            print("-----------")
    print("\n")

def check_win(board, player):
    """Check if the player has won."""
    # Check rows and columns
    for i in range(3):
        if all(board[i][j] == player for j in range(3)):  # Rows
            return True
        if all(board[j][i] == player for j in range(3)):  # Columns
            return True
    
    # Check diagonals
    if all(board[i][i] == player for i in range(3)):  # Main diagonal
        return True
    if all(board[i][2-i] == player for i in range(3)):  # Anti-diagonal
        return True
    
    return False

def is_board_full(board):
    """Check if the board is full (tie)."""
    return all(board[i][j] != ' ' for i in range(3) for j in range(3))

def get_valid_move(board):
    """Get and validate player move."""
    while True:
        try:
            move = int(input("Enter your move (1-9): "))
            if 1 <= move <= 9:
                row = (move - 1) // 3
                col = (move - 1) % 3
                if board[row][col] == ' ':
                    return row, col
                else:
                    print("That position is already taken!")
            else:
                print("Please enter a number between 1 and 9.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def main():
    """Main game function."""
    # Initialize game
    board = [[' ' for _ in range(3)] for _ in range(3)]
    current_player = 'X'
    move_count = 0
    
    print("Welcome to Tic Tac Toe!")
    print("Use numbers 1-9 to make your move as shown below:")
    print_board([['1', '2', '3'], ['4', '5', '6'], ['7', '8', '9']])
    
    # Game loop
    while True:
        print(f"Player {current_player}'s turn")
        row, col = get_valid_move(board)
        board[row][col] = current_player
        move_count += 1
        print_board(board)
        
        # Check win
        if check_win(board, current_player):
            print(f"Player {current_player} wins!")
            break
        
        # Check tie
        if move_count == 9:
            print("It's a tie!")
            break
        
        # Switch player
        current_player = 'O' if current_player == 'X' else 'X'

if __name__ == "__main__":
    main()