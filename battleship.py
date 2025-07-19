import os

# Just setting up some basics for the game
BOARD_SIZE = 5
COLUMN_LABELS = ["A", "B", "C", "D", "E"]  # These are the column letters for the board

# This makes an empty board filled with blank spaces
def create_board(size):
    board = []
    for _ in range(size):
        row = []
        for _ in range(size):
            row.append(" ")
        board.append(row)
    return board

# This shows the board in the terminal
# If hide_ships is True, we won't show the ship positions (used for guessing)
def display_board(board, hide_ships=False):
    print("   A B C D E")
    row_num = 1
    for row in board:
        line = str(row_num) + "  "
        for cell in row:
            if cell == "B" and hide_ships:
                line += "  "  # Don't show ship if it's supposed to be hidden
            else:
                line += cell + " "
        print(line)
        row_num += 1

# Clears the terminal screen to keep things clean
def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

# This turns something like "B3" into row and column numbers we can use
def parse_coordinate(coord):
    if len(coord) < 2:
        return None
    col_letter = coord[0].upper()
    row_str = coord[1:]

    if col_letter not in COLUMN_LABELS:
        return None

    try:
        row = int(row_str) - 1
        col = COLUMN_LABELS.index(col_letter)
    except:
        return None

    # Making sure the guess is actually on the board
    if row < 0 or row >= BOARD_SIZE or col < 0 or col >= BOARD_SIZE:
        return None

    return [row, col]

# This is where the player picks where to put their ship
def place_ship(player_num, board):
    while True:
        clear_screen()
        print("=== Player", player_num, ": Place Your Ship ===")
        display_board(board)
        coord = input("Enter ship location (like B3): ").strip()
        position = parse_coordinate(coord)
        if position is None:
            print("Invalid input. Try again.")
            continue

        row = position[0]
        col = position[1]

        if board[row][col] == " ":
            board[row][col] = "B"  # Place the ship
            break
        else:
            print("That spot is already taken. Try again.")

    input("Ship placed! Press Enter and give the computer to the next player...")
    clear_screen()

# This is one round of guessing (shooting at a spot)
def take_turn(player_num, guess_board, opponent_board):
    print("=== Player", player_num, "'s Turn ===")
    display_board(guess_board)
    while True:
        guess = input("Enter coordinate to fire at (e.g., C2): ").strip()
        position = parse_coordinate(guess)
        if position is None:
            print("Invalid coordinate. Try again.")
            continue

        row = position[0]
        col = position[1]

        if guess_board[row][col] != " ":
            print("You already guessed that spot.")
        else:
            if opponent_board[row][col] == "B":
                print("HIT!")
                guess_board[row][col] = "X"
                opponent_board[row][col] = "X"
                return True
            else:
                print("MISS!")
                guess_board[row][col] = "O"
                opponent_board[row][col] = "O"
                return False

# === Main part of the game ===

# Make boards for each player
player1_board = create_board(BOARD_SIZE)
player2_board = create_board(BOARD_SIZE)
player1_guesses = create_board(BOARD_SIZE)
player2_guesses = create_board(BOARD_SIZE)

# Players each put one ship on their own board
place_ship(1, player1_board)
place_ship(2, player2_board)

# Now the game keeps going until someone hits the other player's ship
while True:
    hit = take_turn(1, player1_guesses, player2_board)
    if hit:
        print("Player 1 wins!")
        break
    input("Press Enter to pass the computer to Player 2...")
    clear_screen()

    hit = take_turn(2, player2_guesses, player1_board)
    if hit:
        print("Player 2 wins!")
        break
    input("Press Enter to pass the computer to Player 1...")
    clear_screen()
