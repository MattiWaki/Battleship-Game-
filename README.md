**Battleship Multiplayer Game**

This is a two-player Battleship game built using Python, sockets, and Pygame. Each player places 5 ships on a 5×5 grid and takes turns guessing the opponent’s ship locations. The game includes a graphical board, sound effects, and a special move called Sonar Pulse that reveals two enemy ships using built-up energy. **More moves will potentially be added in the future.**

**How to Play:**

- The game is played on a 5×5 grid labeled with rows 1–5 and columns A–E (e.g., A3, D5, etc.).

- Each player places 5 ships by typing grid coordinates like B2, D4, etc.

- On your turn, type a coordinate (e.g., C1) to fire a shot at that location.

- You’ll see:

  - "X" for hits,

  - Broken planks for misses,

  - Green dots for sonar-revealed ship locations.

- After each turn, you build energy (up to 3 max).

- When you have at least 1 energy, you can type sonar pulse to reveal 2 hidden enemy ships.

- First player to sink all 5 of the opponent’s ships wins.

**Running the Game Locally (Same Laptop):**

1. Open two terminal windows or tabs.

2. In the first, run: python server.py

3. In the second, run: python client.py

**Running the Game on Two Laptops (with Ngrok):**

1 .Set up Ngrok on the host machine:

 - Download Ngrok: https://ngrok.com/download

 - Authenticate: ngrok config add-authtoken <your_token>

 - Start a TCP tunnel: ngrok tcp 5050

 - Note the forwarded address (e.g., tcp://0.tcp.ngrok.io:12345)

2. Modify the server code:
In server.py, replace:
**server_socket.bind(('localhost', 5050))**
with:
**server_socket.bind(('0.0.0.0', 5050))**
Then run: python server.py

3. Modify the client code:
In client.py, replace:
host = 'localhost'
port = 5050
with:
**host = '0.tcp.ngrok.io' (whatever Ngrok gives you)**
**port = 12345 (whatever Ngrok gives you)**
Then run: python client.py

**Requirements:**

- Python 3.x

- Pygame: pip install pygame

- Ngrok (for remote play)

**Notes:**

- Use valid coordinates like A1, C3, etc.

- Ships can’t overlap.

- Sonar Pulse requires energy and available hidden ships.

- Keep your assets/ folder intact for graphics and audio.

- Match the Ngrok IP and port exactly when connecting.
