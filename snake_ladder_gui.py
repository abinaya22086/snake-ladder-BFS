#!/usr/bin/env python3
import tkinter as tk
from tkinter import messagebox, filedialog
import random
from collections import deque

# ---------------------- Configuration ----------------------
BOARD_SIZE = 10           # 10x10 board (1..100)
CELL_SIZE = 60            # pixels
TOKEN_RADIUS = 12
ANIM_DELAY = 400         # milliseconds between moves when animating

# Sample snakes and ladders mapping: start -> end
# Ladders (up moves) and Snakes (down moves)
BOARD_TRANSITIONS = {
    3: 22,
    5: 8,
    11: 26,
    20: 29,
    27: 1,
    17: 4,    # snake example
    21: 82,
    43: 77,
    50: 91,
    62: 19,   # snake
    66: 87,
    74: 53,   # snake
    80: 99,
    95: 75,   # snake
    96: 84,   # snake
}

# ---------------------- BFS Solver ----------------------
def bfs_min_moves(board_transitions, target=100):
    N = target
    visited = [False]*(N+1)
    parent = [-1]*(N+1)   # store parent position
    parent_move = [-1]*(N+1)  # store dice value used to get here
    q = deque()
    q.append(1)
    visited[1] = True

    while q:
        pos = q.popleft()
        if pos == N:
            break
        for dice in range(1, 7):
            nxt = pos + dice
            if nxt > N:
                continue
            if board_transitions.get(nxt, -1) != -1:
                nxt = board_transitions[nxt]
            if not visited[nxt]:
                visited[nxt] = True
                parent[nxt] = pos
                parent_move[nxt] = dice
                q.append(nxt)

    if not visited[N]:
        return None  # unreachable (shouldn't happen in normal boards)

    # reconstruct path positions from 1 to N using parents
    path_positions = []
    cur = N
    while cur != -1:
        path_positions.append(cur)
        cur = parent[cur]
    path_positions.reverse()

    # reconstruct dice values between positions (approximate: show dice that moved)
    dice_sequence = []
    for i in range(1, len(path_positions)):
        dice_sequence.append(parent_move[path_positions[i]])

    return {
        'moves': len(dice_sequence),
        'positions': path_positions,
        'dice': dice_sequence
    }

# ---------------------- GUI Application ----------------------
class SnakeLadderApp:
    def __init__(self, root):
        self.root = root
        root.title("Snake & Ladder - Playable + BFS Solver")
        self.board_transitions = BOARD_TRANSITIONS.copy()
        self.create_widgets()
        self.reset_game()

    def create_widgets(self):
        # Canvas for board
        self.canvas = tk.Canvas(self.root, width=CELL_SIZE*BOARD_SIZE+200, height=CELL_SIZE*BOARD_SIZE, bg='white')
        self.canvas.grid(row=0, column=0, padx=10, pady=10, rowspan=6)

        # Draw board grid and numbers
        self.draw_board()

        # Side panel buttons and log
        self.roll_btn = tk.Button(self.root, text="Roll Dice", command=self.player_roll, width=20)
        self.roll_btn.grid(row=0, column=1, padx=10, pady=6, sticky='n')

        self.ai_btn = tk.Button(self.root, text="AI Solve (BFS)", command=self.run_ai_solve, width=20)
        self.ai_btn.grid(row=1, column=1, padx=10, pady=6, sticky='n')

        self.reset_btn = tk.Button(self.root, text="Reset", command=self.reset_game, width=20)
        self.reset_btn.grid(row=2, column=1, padx=10, pady=6, sticky='n')

        self.save_btn = tk.Button(self.root, text="Save Board Copy", command=self.save_board_copy, width=20)
        self.save_btn.grid(row=3, column=1, padx=10, pady=6, sticky='n')

        tk.Label(self.root, text="Log:", font=('Arial',10,'bold')).grid(row=4, column=1, sticky='nw', padx=10)
        self.log_text = tk.Text(self.root, width=30, height=18, state='disabled')
        self.log_text.grid(row=5, column=1, padx=10, pady=6, sticky='n')

    def draw_board(self):
        self.cells = {}
        N = BOARD_SIZE*BOARD_SIZE
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                # calculate number in snake-ladder pattern
                row_from_bottom = BOARD_SIZE - 1 - r
                if (row_from_bottom % 2) == 0:
                    num = row_from_bottom*BOARD_SIZE + (c+1)
                else:
                    num = row_from_bottom*BOARD_SIZE + (BOARD_SIZE - c)

                x1 = c*CELL_SIZE
                y1 = r*CELL_SIZE
                x2 = x1 + CELL_SIZE
                y2 = y1 + CELL_SIZE
                rect = self.canvas.create_rectangle(x1, y1, x2, y2, fill='ivory', outline='black')
                self.canvas.create_text(x1+6, y1+6, anchor='nw', text=str(num), font=('Arial',9,'bold'))
                self.cells[num] = (x1, y1, x2, y2)
        # draw snakes and ladders visually as lines/arcs
        for start, end in self.board_transitions.items():
            self.draw_transition(start, end)

    def draw_transition(self, start, end):
        x1, y1, x2, y2 = self.cells[start]
        sx = (x1+x2)/2
        sy = (y1+y2)/2
        x1e, y1e, x2e, y2e = self.cells[end]
        ex = (x1e+x2e)/2
        ey = (y1e+y2e)/2
        color = 'green' if end>start else 'red'
        self.canvas.create_line(sx, sy, ex, ey, width=3, arrow='last', fill=color)
        # label
        self.canvas.create_text((sx+ex)/2, (sy+ey)/2, text=f"{start}->{end}", font=('Arial',8,'italic'))

    def reset_game(self):
        # player position and token
        self.player_pos = 1
        self.ai_path = None
        self.ai_animating = False
        self.canvas.delete('token')
        self.draw_token(self.player_pos, tag='token')
        self.log("Game reset. Player at 1.")

    def draw_token(self, position, tag='token'):
        # remove existing token with the same tag
        self.canvas.delete(tag)
        x1, y1, x2, y2 = self.cells[position]
        cx = (x1+x2)/2
        cy = (y1+y2)/2
        # draw token as a circle
        self.canvas.create_oval(cx-TOKEN_RADIUS, cy-TOKEN_RADIUS, cx+TOKEN_RADIUS, cy+TOKEN_RADIUS, fill='blue', tags=tag)
        # write pos inside small text
        self.canvas.create_text(cx, cy, text=str(position), fill='white', font=('Arial',9,'bold'), tags=tag)

    def player_roll(self):
        if self.ai_animating:
            return
        dice = random.randint(1,6)
        self.log(f"Player rolls: {dice}")
        newpos = self.player_pos + dice
        if newpos > 100:
            newpos = self.player_pos  # can't move
            self.log("Roll exceeds 100: no move.")
        else:
            if self.board_transitions.get(newpos, -1) != -1:
                dest = self.board_transitions[newpos]
                self.log(f"Hit {'Ladder' if dest>newpos else 'Snake'}: {newpos}->{dest}")
                newpos = dest
        self.player_pos = newpos
        self.draw_token(self.player_pos, tag='token')
        if self.player_pos == 100:
            self.log("Player reached 100! You win!")
            messagebox.showinfo("Victory", "Player reached the end!")

    def run_ai_solve(self):
        if self.ai_animating:
            return
        self.log("AI BFS solving...")
        result = bfs_min_moves(self.board_transitions, target=100)
        if result is None:
            self.log("AI: No path to 100 found.")
            return
        self.ai_path = result['positions']
        dice_seq = result['dice']
        self.log(f"AI found solution in {result['moves']} moves.")
        self.log(f"Positions: {self.ai_path}")
        # animate token along path
        self.ai_animating = True
        # create a separate token for AI visualization
        self.animate_ai(0)

    def animate_ai(self, idx):
        if not self.ai_animating or self.ai_path is None:
            return
        if idx >= len(self.ai_path):
            self.ai_animating = False
            self.log("AI animation complete.")
            return
        pos = self.ai_path[idx]
        # use different tag so player token stays
        self.draw_token(pos, tag='ai_token')
        # log step
        if idx>0:
            self.log(f"AI moved to {pos}")
        # schedule next move
        self.root.after(ANIM_DELAY, lambda: self.animate_ai(idx+1))

    def save_board_copy(self):
        # allow user to save a snapshot of the current canvas as postscript
        file = filedialog.asksaveasfilename(defaultextension='.ps', filetypes=[('PostScript', '*.ps')], title='Save Board Snapshot')
        if not file:
            return
        try:
            self.canvas.postscript(file=file)
            messagebox.showinfo("Saved", f"Board snapshot saved to:\n{file}\n(You can convert .ps to .png using image tools)")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save: {e}")

    def log(self, text):
        self.log_text.config(state='normal')
        self.log_text.insert('end', text + '\n')
        self.log_text.see('end')
        self.log_text.config(state='disabled')


if __name__ == '__main__':
    root = tk.Tk()
    app = SnakeLadderApp(root)
    root.mainloop()
