import threading
import os
import time
import pygame
import sys
import socket

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
pygame.display.set_caption("Battleship (Client)")
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

# === NETWORK SETUP (CLIENT) ===
time.sleep(2)  # Give server time to start
host = 'localhost'  # Replace with actual ngrok host
port = 5050
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((host, port))
print("Connected to server.")

# === GAME SETUP ===
player_board = create_board(BOARD_SIZE)
guess_board = create_board(BOARD_SIZE)

# === SHIP PLACEMENT ===
if client_socket.recv(1024).decode() == "PLACE_SHIP":
    while True:
        draw_board_pygame(player_board, show_ships=True)
        coord = input("Enter ship location (like B3): ").strip()
        pos = parse_coordinate(coord)
        if pos and player_board[pos[0]][pos[1]] == " ":
            player_board[pos[0]][pos[1]] = "B"
            draw_board_pygame(player_board, show_ships=True)
            client_socket.sendall(coord.encode())
            break
        print("Invalid or occupied. Try again.")
    os.system("clear")

# === GAME ANIMATION ===
def show_message(screen, message, duration=1500, font_size=50):
    font = pygame.font.SysFont(None, font_size)
    text = font.render(message, True, (255, 255, 255))
    rect = text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
    screen.fill((0, 0, 0))
    screen.blit(text, rect)
    pygame.display.flip()
    pygame.time.wait(duration)

# === GAME LOOP ===
while True:
    # Opponent's turn
    show_message(screen, "Heading Back...", duration=1000)
    draw_board_pygame(player_board, show_ships=True)
    print("Waiting for opponent's move...")
    guess = client_socket.recv(1024).decode()
    pos = parse_coordinate(guess)

    if player_board[pos[0]][pos[1]] == "B":
        player_board[pos[0]][pos[1]] = "X"
        draw_board_pygame(player_board, show_ships=True)
        print(f"Opponent guessed {guess} — they hit your ship!")
        client_socket.sendall(b"HIT")
        pygame.time.wait(2000)
        print("You lose!")
        break
    else:
        player_board[pos[0]][pos[1]] = "O"
        draw_board_pygame(player_board, show_ships=True)
        print(f"Opponent guessed {guess} — they missed.")
        client_socket.sendall(b"MISS")
        pygame.time.wait(2000)

    # Your turn
    show_message(screen, "Attack!", duration=1000)
    draw_board_pygame(guess_board, show_ships=False)
    your_guess = input("Your guess (e.g. D4): ").strip()
    client_socket.sendall(your_guess.encode())
    result = client_socket.recv(1024).decode()
    pos = parse_coordinate(your_guess)

    if result == "HIT":
        print("You hit!")
        guess_board[pos[0]][pos[1]] = "X"
        draw_board_pygame(guess_board)
        pygame.time.wait(2000)
    elif result == "MISS":
        print("You missed.")
        guess_board[pos[0]][pos[1]] = "O"
        draw_board_pygame(guess_board)
        pygame.time.wait(2000)
    elif result == "LOSE":
        print("You win!")
        guess_board[pos[0]][pos[1]] = "X"
        draw_board_pygame(guess_board)
        pygame.time.wait(2000)
        break


