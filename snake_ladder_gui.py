import tkinter as tk
from tkinter import messagebox
import random
import time
from PIL import Image, ImageTk

# Board setup
BOARD_SIZE = 10
CELL_SIZE = 60
BOARD_WIDTH = BOARD_SIZE * CELL_SIZE
BOARD_HEIGHT = BOARD_SIZE * CELL_SIZE

# Snakes and ladders (start -> end)
SNAKES = {99: 80, 95: 75, 92: 88, 74: 53, 64: 60, 62: 19, 49: 11, 46: 25, 16: 6}
LADDERS = {2: 38, 7: 14, 8: 31, 15: 26, 21: 82, 28: 84, 36: 44, 51: 67, 71: 91, 78: 98, 87: 94}

class SnakeAndLadderGame:
    def __init__(self, root):
        self.root = root
        self.root.title("🐍 Snake & Ladder – BFS Solver 🎲")
        self.root.configure(bg="#1f1f2e")

        self.canvas = tk.Canvas(root, width=BOARD_WIDTH, height=BOARD_HEIGHT, bg="white", highlightthickness=0)
        self.canvas.grid(row=0, column=0, padx=20, pady=20)

        self.sidebar = tk.Frame(root, bg="#1f1f2e")
        self.sidebar.grid(row=0, column=1, sticky="ns")

        # Buttons
        self.roll_btn = tk.Button(self.sidebar, text="🎲 Roll Dice", font=("Arial", 12, "bold"),
                                  bg="#4a90e2", fg="white", width=15, command=self.roll_dice)
        self.roll_btn.pack(pady=8)

        self.solve_btn = tk.Button(self.sidebar, text="🤖 AI Solve (BFS)", font=("Arial", 12, "bold"),
                                   bg="#2ecc71", fg="white", width=15, command=self.ai_solve)
        self.solve_btn.pack(pady=8)

        self.reset_btn = tk.Button(self.sidebar, text="🔄 Reset Game", font=("Arial", 12, "bold"),
                                   bg="#e74c3c", fg="white", width=15, command=self.reset_game)
        self.reset_btn.pack(pady=8)

        # Log area
        tk.Label(self.sidebar, text="📜 Game Log", fg="#00ffcc", bg="#1f1f2e",
                 font=("Consolas", 13, "bold")).pack(pady=(15, 0))
        self.log = tk.Text(self.sidebar, height=20, width=40, bg="#2b2b3d", fg="white", font=("Consolas", 10))
        self.log.pack(padx=10, pady=10)

        # Load assets
        try:
            self.snake_img = Image.open("assets/snake.png")
            self.ladder_img = Image.open("assets/ladder.png")
            self.snake_img = self.snake_img.resize((80, 80))
            self.ladder_img = self.ladder_img.resize((80, 80))
            self.snake_photo = ImageTk.PhotoImage(self.snake_img)
            self.ladder_photo = ImageTk.PhotoImage(self.ladder_img)
        except:
            self.snake_photo = None
            self.ladder_photo = None

        # Draw board
        self.draw_board()

        # Initialize player
        self.player_pos = 1
        self.player_token = self.canvas.create_oval(5, BOARD_HEIGHT - CELL_SIZE + 5, 35, BOARD_HEIGHT - 25, fill="blue")
        self.log_message("🎮 Game started! Player at position 1.")

    def log_message(self, message):
        self.log.insert(tk.END, message + "\n")
        self.log.see(tk.END)

    def get_coordinates(self, position):
        row = (position - 1) // BOARD_SIZE
        col = (position - 1) % BOARD_SIZE
        if row % 2 == 1:
            col = BOARD_SIZE - 1 - col
        x = col * CELL_SIZE + CELL_SIZE / 2
        y = BOARD_HEIGHT - (row * CELL_SIZE + CELL_SIZE / 2)
        return x, y

    def draw_board(self):
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                x1 = col * CELL_SIZE
                y1 = row * CELL_SIZE
                x2 = x1 + CELL_SIZE
                y2 = y1 + CELL_SIZE
                color = "#fefefe" if (row + col) % 2 == 0 else "#e6e6e6"
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="black")

                # Calculate number in snake pattern
                num = BOARD_SIZE * (BOARD_SIZE - row - 1) + (col + 1 if (BOARD_SIZE - row) % 2 == 1 else BOARD_SIZE - col)
                self.canvas.create_text(x1 + 10, y1 + 10, text=str(num), anchor="nw", font=("Arial", 8, "bold"))

        # Draw ladders
        if self.ladder_photo:
            for start, end in LADDERS.items():
                x1, y1 = self.get_coordinates(start)
                x2, y2 = self.get_coordinates(end)
                self.canvas.create_image((x1 + x2) / 2, (y1 + y2) / 2, image=self.ladder_photo)
        else:
            for start, end in LADDERS.items():
                x1, y1 = self.get_coordinates(start)
                x2, y2 = self.get_coordinates(end)
                self.canvas.create_line(x1, y1, x2, y2, fill="green", width=4, arrow=tk.LAST)

        # Draw snakes
        if self.snake_photo:
            for start, end in SNAKES.items():
                x1, y1 = self.get_coordinates(start)
                x2, y2 = self.get_coordinates(end)
                self.canvas.create_image((x1 + x2) / 2, (y1 + y2) / 2, image=self.snake_photo)
        else:
            for start, end in SNAKES.items():
                x1, y1 = self.get_coordinates(start)
                x2, y2 = self.get_coordinates(end)
                self.canvas.create_line(x1, y1, x2, y2, fill="red", width=4, arrow=tk.LAST)

    def roll_dice(self):
        dice = random.randint(1, 6)
        self.log_message(f"🎲 Player rolled a {dice}")
        self.move_player(dice)

    def move_player(self, steps):
        new_pos = self.player_pos + steps
        if new_pos > 100:
            new_pos = self.player_pos
        if new_pos in SNAKES:
            self.log_message(f"🐍 Bitten! Go down from {new_pos} → {SNAKES[new_pos]}")
            new_pos = SNAKES[new_pos]
        elif new_pos in LADDERS:
            self.log_message(f"🪜 Climb ladder {self.player_pos + steps} → {LADDERS[new_pos]}")
            new_pos = LADDERS[new_pos]

        self.player_pos = new_pos
        self.animate_player(new_pos)
        if new_pos == 100:
            messagebox.showinfo("🏁 Game Over", "🎉 You reached 100! You win!")
            self.reset_game()

    def animate_player(self, position):
        x, y = self.get_coordinates(position)
        self.canvas.coords(self.player_token, x - 15, y - 15, x + 15, y + 15)
        self.root.update()
        time.sleep(0.3)

    def bfs_solve(self):
        queue = [(1, [1])]
        visited = set()
        while queue:
            pos, path = queue.pop(0)
            if pos == 100:
                return path
            for dice in range(1, 7):
                next_pos = pos + dice
                if next_pos > 100:
                    continue
                if next_pos in SNAKES:
                    next_pos = SNAKES[next_pos]
                elif next_pos in LADDERS:
                    next_pos = LADDERS[next_pos]
                if next_pos not in visited:
                    visited.add(next_pos)
                    queue.append((next_pos, path + [next_pos]))
        return []

    def ai_solve(self):
        self.log_message("🤖 AI BFS solving...")
        path = self.bfs_solve()
        if path:
            self.log_message(f"✅ AI found solution in {len(path)-1} moves.")
            for p in path[1:]:
                self.animate_player(p)
            self.log_message("🧠 AI animation complete.")
        else:
            self.log_message("⚠️ No path found.")

    def reset_game(self):
        self.player_pos = 1
        x, y = self.get_coordinates(1)
        self.canvas.coords(self.player_token, x - 15, y - 15, x + 15, y + 15)
        self.log.delete(1.0, tk.END)
        self.log_message("🔄 Game reset. Player at position 1.")

if __name__ == "__main__":
    root = tk.Tk()
    game = SnakeAndLadderGame(root)
    root.mainloop()
