import socket
import threading
import os

BOARD_SIZE = 5
COLUMN_LABELS = ["A", "B", "C", "D", "E"]

def create_board(size):
    return [[" " for _ in range(size)] for _ in range(size)]

def display_board(board):
    print("   A B C D E")
    for i, row in enumerate(board):
        print(f"{i+1}  {' '.join(row)}")

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
    if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE:
        return [row, col]
    return None

def place_ship(board):
    while True:
        display_board(board)
        coord = input("Enter ship location (like B3): ").strip()
        pos = parse_coordinate(coord)
        if pos and board[pos[0]][pos[1]] == " ":
            board[pos[0]][pos[1]] = "B"
            break
        print("Invalid or occupied. Try again.")
    os.system("clear")
    print("Waiting for opponent to choose their ship location...")


# === NETWORK SETUP (SERVER) ===
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('localhost', 5050))
server_socket.listen(1)
print("Waiting for connection...")
conn, addr = server_socket.accept()
print("Client connected.")

# === GAME START ===
player1_board = create_board(BOARD_SIZE)
player2_board = create_board(BOARD_SIZE)
player1_guesses = create_board(BOARD_SIZE)
player2_guesses = create_board(BOARD_SIZE)

# Player 1 places ship
place_ship(player1_board)

# Tell client to place ship
conn.sendall(b'PLACE_SHIP')
client_ship = conn.recv(1024).decode().strip()
pos = parse_coordinate(client_ship)
if pos:
    player2_board[pos[0]][pos[1]] = "B"

# GAME LOOP
while True:
    # Player 1 turn
    display_board(player1_guesses)
    guess = input("Your guess (e.g. C2): ").strip()
    conn.sendall(guess.encode())
    result = conn.recv(1024).decode()
    pos = parse_coordinate(guess)
    if result == "HIT":
        print("You hit!")
        player1_guesses[pos[0]][pos[1]] = "X"
        print("You win!")
        conn.sendall(b'LOSE')
        break
    else:
        print("You missed.")
        player1_guesses[pos[0]][pos[1]] = "O"

    # Wait for opponent guess
    print("Waiting for opponent's move...")
    opponent_guess = conn.recv(1024).decode()
    pos = parse_coordinate(opponent_guess)
    if player1_board[pos[0]][pos[1]] == "B":
        player1_board[pos[0]][pos[1]] = "X"
        conn.sendall(b"HIT")
        print(f"Opponent guessed {opponent_guess} — they hit your ship!")
        print("You lose!")
        break
    else:
        player1_board[pos[0]][pos[1]] = "O"
        conn.sendall(b"MISS")
        print(f"Opponent guessed {opponent_guess} — they missed.")
