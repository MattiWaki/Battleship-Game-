import socket
import os
import time
import pygame
import sys
import random
import base64

# === CONFIG ===
BOARD_SIZE = 5
CELL_SIZE = 100
SCREEN_SIZE = BOARD_SIZE * CELL_SIZE
COLUMN_LABELS = ["A", "B", "C", "D", "E"]
SONAR_COST = 1

# === COLORS ===
BLUE = (30, 144, 255)
DARK_BLUE = (0, 0, 139)
WHITE = (255, 255, 255)

# === INIT PYGAME ===
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE))
pygame.display.set_caption("Battleship (Client)")
font = pygame.font.SysFont(None, 48)

# === BACKGROUND AUDIO ===
pygame.mixer.music.load("assets/57442525_pirates-and-rum-cinematic_by_blackalexstudio_preview.mp3")
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)
explosion_sound = pygame.mixer.Sound("assets/explosion-fx-343683.mp3")
explosion_sound.set_volume(0.7)

# === Load Ship Image ===
try:
    ship_image = pygame.image.load("assets/—Pngtree—small boat_7143559.png")
    ship_image = pygame.transform.scale(ship_image, (CELL_SIZE, CELL_SIZE))
except:
    print("Warning: Could not load ship image. Using placeholder.")
    ship_image = pygame.Surface((CELL_SIZE, CELL_SIZE))
    ship_image.fill((255, 0, 0))  # Red square as placeholder

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
            elif symbol == "S":  # Sonar reveal
                pygame.draw.circle(screen, (0, 255, 0), rect.center, CELL_SIZE//3)

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

# === NETWORK SETUP ===
time.sleep(2)  # Give server time to start
host = 'localhost'
port = 5050
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((host, port))
print("Connected to server.")
print("Waiting for opponent to place their ship...")

# === GAME SETUP ===
player_board = create_board(BOARD_SIZE)
guess_board = create_board(BOARD_SIZE)
opponent_ships = []
energy = 0

# === SHIP PLACEMENT ===
if client_socket.recv(1024).decode() == "PLACE_SHIPS":
    placed = 0
    ship_coords = []

    while placed < 5:
        draw_board_pygame(player_board, show_ships=True)
        coord = input(f"Enter location for ship #{placed + 1} (like B3): ").strip()
        pos = parse_coordinate(coord)
        if pos and player_board[pos[0]][pos[1]] == " ":
            player_board[pos[0]][pos[1]] = "B"
            ship_coords.append(coord.upper())
            placed += 1
            client_socket.sendall(coord.encode())
            ack = client_socket.recv(1024)  # Wait for ack
        else:
            print("Invalid or occupied. Try again.")

    draw_board_pygame(player_board, show_ships=True)
    os.system("clear")

    # Receive secret ship locations from server
    while True:
        data = client_socket.recv(1024).decode()
        if data.startswith("SECRET_SHIPS:"):
            secret_data = data[len("SECRET_SHIPS:"):]
            secret_ship_locations = base64.b64decode(secret_data.encode()).decode().split(",")
            opponent_ships = [parse_coordinate(coord) for coord in secret_ship_locations]
            break

def show_message(screen, message, duration=1500, font_size=50):
    font = pygame.font.SysFont(None, font_size)
    text = font.render(message, True, (255, 255, 255))
    rect = text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
    screen.fill((0, 0, 0))
    screen.blit(text, rect)
    pygame.display.flip()
    pygame.time.wait(duration)

# === GAME LOOP ===
player_hits = 0
opponent_hits = 0
TOTAL_SHIPS = 5

while True:
    # Opponent's turn
    show_message(screen, "Heading Back...", duration=1000)
    draw_board_pygame(player_board, show_ships=True)
    print("Waiting for opponent's move...")
    guess = client_socket.recv(1024).decode()
    pos = parse_coordinate(guess)

    if player_board[pos[0]][pos[1]] == "B":
        player_board[pos[0]][pos[1]] = "X"
        explosion_sound.play()
        opponent_hits += 1
        draw_board_pygame(player_board, show_ships=True)
        print(f"Opponent guessed {guess} — they hit your ship!")
        if opponent_hits == TOTAL_SHIPS:
            client_socket.sendall(b'LOSE')
            pygame.time.wait(2000)
            print("You lose!")
            break
        else:
            client_socket.sendall(b'HIT')
            pygame.time.wait(2000)
    else:
        player_board[pos[0]][pos[1]] = "O"
        draw_board_pygame(player_board, show_ships=True)
        print(f"Opponent guessed {guess} — they missed.")
        client_socket.sendall(b'MISS')
        pygame.time.wait(2000)
    
    # Gain energy after each turn
    energy = min(energy + 0.3, 3)

    # Your turn
    show_message(screen, "Attack!", duration=1000)
    draw_board_pygame(guess_board, show_ships=False)

    # Special move option
    print(f"\n⚡ Energy Available: {energy}")
    print("Available Special Moves:")
    print(" - 'Sonar Pulse' (cost: 1 energy): Reveals 2 enemy ship positions.")
    special_move = input("Type a move name to use it, or press Enter to skip: ").strip().lower()

    if special_move == "sonar pulse":
        if energy >= SONAR_COST:
            hidden_ships = [
                pos for pos in opponent_ships
                if guess_board[pos[0]][pos[1]] == " "
            ]
            if hidden_ships:
                reveal_count = min(2, len(hidden_ships))
                revealed = random.sample(hidden_ships, reveal_count)
                print("\n📡 Sonar Pulse activated! Revealed enemy ships at:")
                for r, c in revealed:
                    coord = f"{COLUMN_LABELS[c]}{r+1}"
                    print(f" - {coord}")
                    guess_board[r][c] = "S"  # Mark as sonar-revealed
                draw_board_pygame(guess_board)
                pygame.time.wait(2000)
                energy -= SONAR_COST
            else:
                print("No hidden enemy ships left to reveal.")
        else:
            print("❌ Not enough energy to use Sonar Pulse.")

    # Normal attack
    your_guess = input("Your guess (e.g. D4): ").strip()
    client_socket.sendall(your_guess.encode())
    result = client_socket.recv(1024).decode()
    pos = parse_coordinate(your_guess)

    if result == "HIT":
        print("You hit!")
        explosion_sound.play()
        guess_board[pos[0]][pos[1]] = "X"
        player_hits += 1
        draw_board_pygame(guess_board)
        pygame.time.wait(2000)
        if player_hits == TOTAL_SHIPS:
            print("You win!")
            break
    elif result == "MISS":
        print("You missed.")
        guess_board[pos[0]][pos[1]] = "O"
        draw_board_pygame(guess_board)
        pygame.time.wait(2000)
    elif result == "LOSE":
        print("You hit and sunk their last ship!")
        guess_board[pos[0]][pos[1]] = "X"
        draw_board_pygame(guess_board)
        pygame.time.wait(2000)
        print("You win!")
        break


client_socket.close()
pygame.quit()