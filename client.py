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

# === NETWORK SETUP (CLIENT) ===
import time
time.sleep(2)  # Give server time to start
host = 'localhost'  # Replace with actual ngrok forwarding address
port = 5050
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((host, port))
print("Connected to server.")

# GAME SETUP
player_board = create_board(BOARD_SIZE)
guess_board = create_board(BOARD_SIZE)

# Wait for server to prompt ship placement
if client_socket.recv(1024).decode() == "PLACE_SHIP":
    while True:
        display_board(player_board)
        coord = input("Enter ship location (like B3): ").strip()
        pos = parse_coordinate(coord)
        if pos and player_board[pos[0]][pos[1]] == " ":
            player_board[pos[0]][pos[1]] = "B"
            client_socket.sendall(coord.encode())
            break
        print("Invalid or occupied. Try again.")
    os.system("clear")

# GAME LOOP
while True:
    # Wait for opponent guess
    print("Waiting for opponent's move...")
    guess = client_socket.recv(1024).decode()
    pos = parse_coordinate(guess)
    if player_board[pos[0]][pos[1]] == "B":
        player_board[pos[0]][pos[1]] = "X"
        client_socket.sendall(b"HIT")
        print(f"Opponent guessed {guess} — they hit your ship!")
        print("You lose!")
        break
    else:
        player_board[pos[0]][pos[1]] = "O"
        client_socket.sendall(b"MISS")
        print(f"Opponent guessed {guess} — they missed.")

    # Your turn
    display_board(guess_board)
    your_guess = input("Your guess (e.g. D4): ").strip()
    client_socket.sendall(your_guess.encode())
    result = client_socket.recv(1024).decode()
    pos = parse_coordinate(your_guess)
    if result == "HIT":
        print("You hit!")
        guess_board[pos[0]][pos[1]] = "X"
    elif result == "MISS":
        print("You missed.")
        guess_board[pos[0]][pos[1]] = "O"
    elif result == "LOSE":
        print("You win!")
        break
