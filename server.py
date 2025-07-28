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

def place_ships(board, num_ships=5):
    placed = 0
    while placed < num_ships:
        draw_board_pygame(board, show_ships=True)
        coord = input(f"Enter location for ship #{placed + 1} (e.g. B3): ").strip()
        pos = parse_coordinate(coord)
        if pos and board[pos[0]][pos[1]] == " ":
            board[pos[0]][pos[1]] = "B"
            placed += 1
        else:
            print("Invalid or occupied. Try again.")
    os.system("clear")
    print("Waiting for opponent to choose their ship locations...")


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

# Player 1 places ships
place_ships(player1_board, num_ships=5)
draw_board_pygame(player1_board, show_ships=True)

# Tell client to place ships
conn.sendall(b'PLACE_SHIPS')

# Receive 5 ship coordinates from client
waiting_for_client_ship = True
conn.settimeout(0.5)
received_ships = 0
while waiting_for_client_ship:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    draw_board_pygame(player1_board, show_ships=True)

    try:
        client_data = conn.recv(1024).decode().strip()
        if client_data:
            coords = client_data.split(",")
            for coord in coords:
                pos = parse_coordinate(coord)
                if pos:
                    player2_board[pos[0]][pos[1]] = "B"
                    received_ships += 1
            if received_ships == 5:
                waiting_for_client_ship = False
    except socket.timeout:
        pass
    except Exception as e:
        print("Connection error:", e)
        pygame.quit()
        sys.exit()
conn.settimeout(None)

print("Both players have placed their ships. Starting game...")

# === GAME ANIMATIONS ===
def show_message(screen, message, duration=1500, font_size=50):
    font = pygame.font.SysFont(None, font_size)
    text = font.render(message, True, (255, 255, 255))
    rect = text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
    screen.fill((0, 0, 0))  # Clear screen with black
    screen.blit(text, rect)
    pygame.display.flip()
    pygame.time.wait(duration)

# === GAME LOOP ===
player1_hits = 0
player2_hits = 0
TOTAL_SHIPS = 5

while True:
    # Player 1's turn (you)
    show_message(screen, "Attack!", duration=1000)
    draw_board_pygame(player1_guesses, show_ships=False)
    guess = input("Your guess (e.g. C2): ").strip()
    conn.sendall(guess.encode())
    result = conn.recv(1024).decode()
    pos = parse_coordinate(guess)

    if result == "HIT":
        print("You hit!")
        player1_guesses[pos[0]][pos[1]] = "X"
        player1_hits += 1
        draw_board_pygame(player1_guesses, show_ships=False)
        pygame.time.wait(2000)
        if player1_hits == TOTAL_SHIPS:
            print("You win!")
            conn.sendall(b'LOSE')
            draw_board_pygame(player1_guesses, show_ships=False)
            break
    elif result == "MISS":
        print("You missed.")
        player1_guesses[pos[0]][pos[1]] = "O"
        draw_board_pygame(player1_guesses, show_ships=False)
        pygame.time.wait(2000)
    elif result == "LOSE":
        print("You hit and sunk their last ship!")
        player1_guesses[pos[0]][pos[1]] = "X"
        draw_board_pygame(player1_guesses, show_ships=False)
        pygame.time.wait(2000)
        print("You win!")
        break

    # Opponent's turn
    show_message(screen, "Heading Back...", duration=1000)
    draw_board_pygame(player1_board, show_ships=True)
    print("Waiting for opponent's move...")
    opponent_guess = conn.recv(1024).decode()
    pos = parse_coordinate(opponent_guess)

    if player1_board[pos[0]][pos[1]] == "B":
        player1_board[pos[0]][pos[1]] = "X"
        player2_hits += 1
        draw_board_pygame(player1_board, show_ships=True)
        print(f"Opponent guessed {opponent_guess} — they hit your ship!")
        if player2_hits == TOTAL_SHIPS:
            conn.sendall(b'LOSE')
            pygame.time.wait(2000)
            print("You lose!")
            break
        else:
            conn.sendall(b'HIT')
            pygame.time.wait(2000)
    else:
        player1_board[pos[0]][pos[1]] = "O"
        draw_board_pygame(player1_board, show_ships=True)
        print(f"Opponent guessed {opponent_guess} — they missed.")
        conn.sendall(b'MISS')
        pygame.time.wait(2000)
