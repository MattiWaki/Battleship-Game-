import socket
import threading
import os
import pygame
import sys

# === CONFIG ===
BOARD_SIZE = 5
CELL_SIZE = 100
SCREEN_SIZE = BOARD_SIZE * CELL_SIZE
COLUMN_LABELS = ["A", "B", "C", "D", "E"]

# === COLORS ===
BLUE = (30, 144, 255)
DARK_BLUE = (0, 0, 139)
WHITE = (255, 255, 255)

# === INIT PYGAME ===
pygame.init()
screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE))
pygame.display.set_caption("Battleship (Server)")
font = pygame.font.SysFont(None, 48)

# === Load Ship Image ===
ship_image = pygame.image.load("/Users/josephacquah/Battleship-Game-/assets/—Pngtree—small boat_7143559.png")
ship_image = pygame.transform.scale(ship_image, (CELL_SIZE, CELL_SIZE))

def create_board(size):
    return [[" " for _ in range(size)] for _ in range(size)]

def draw_board_pygame(board, show_ships=False):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            color = BLUE if (row + col) % 2 == 0 else DARK_BLUE
            rect = pygame.Rect(col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, color, rect)

            symbol = board[row][col]
            if symbol == "B" and show_ships:
                screen.blit(ship_image, rect)
            elif symbol in ["X", "O"]:
                text = font.render(symbol, True, WHITE)
                text_rect = text.get_rect(center=rect.center)
                screen.blit(text, text_rect)

    pygame.display.flip()

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
        draw_board_pygame(board, show_ships=True)
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
draw_board_pygame(player1_board, show_ships=True)  # Show own ship immediately

# Tell client to place ship
conn.sendall(b'PLACE_SHIP')

# Wait for client to place ship while showing player 1's ship and keeping window responsive
waiting_for_client_ship = True
conn.settimeout(0.5)
while waiting_for_client_ship:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    draw_board_pygame(player1_board, show_ships=True)

    try:
        client_ship = conn.recv(1024).decode().strip()
        if client_ship:
            pos = parse_coordinate(client_ship)
            if pos:
                player2_board[pos[0]][pos[1]] = "B"
                waiting_for_client_ship = False
    except socket.timeout:
        pass
    except Exception as e:
        print("Connection error:", e)
        pygame.quit()
        sys.exit()
conn.settimeout(None)

print("Both players have placed their ships. Starting game...")

# === GAME LOOP ===
while True:
    # Player 1's turn (you)
    draw_board_pygame(player1_guesses, show_ships=False)
    guess = input("Your guess (e.g. C2): ").strip()
    conn.sendall(guess.encode())
    result = conn.recv(1024).decode()
    pos = parse_coordinate(guess)

    if result == "HIT":
        print("You hit!")
        player1_guesses[pos[0]][pos[1]] = "X"
        draw_board_pygame(player1_guesses, show_ships=False)
        pygame.time.wait(2000)
        print("You win!")
        draw_board_pygame(player1_guesses, show_ships=False)
        conn.sendall(b'LOSE')
        break
    else:
        print("You missed.")
        player1_guesses[pos[0]][pos[1]] = "O"
        draw_board_pygame(player1_guesses, show_ships=False)
        pygame.time.wait(2000)
        draw_board_pygame(player1_guesses, show_ships=False)

    # Opponent's turn
    draw_board_pygame(player1_board, show_ships=True)
    print("Waiting for opponent's move...")
    opponent_guess = conn.recv(1024).decode()
    pos = parse_coordinate(opponent_guess)

    if player1_board[pos[0]][pos[1]] == "B":
        player1_board[pos[0]][pos[1]] = "X"
        draw_board_pygame(player1_board, show_ships=True)
        print(f"Opponent guessed {opponent_guess} — they hit your ship!")
        conn.sendall(b"HIT")  # 🔁 Send immediately
        pygame.time.wait(2000)  # ⏱ Then pause
        draw_board_pygame(player1_board, show_ships=True)
        print("You lose!")
        break
    else:
        player1_board[pos[0]][pos[1]] = "O"
        draw_board_pygame(player1_board, show_ships=True)
        print(f"Opponent guessed {opponent_guess} — they missed.")
        conn.sendall(b"MISS")  # 🔁 Send immediately
        pygame.time.wait(2000)  # ⏱ Then pause
        draw_board_pygame(player1_board, show_ships=True)