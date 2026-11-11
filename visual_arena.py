import copy
import random
import tkinter as tk
from tkinter import ttk, messagebox

import numpy as np

from problems import ConnectFour, Othello
from algorithms import MinimaxAgent, MCTSAgent


class VisualArena:
    COLORS = {0: "#E9EEF6", 1: "#F48CA7", -1: "#77B5F5"}

    def __init__(self, root):
        self.root = root
        root.title("AI Game Arena | Minimax vs MCTS")
        root.geometry("850x800")
        root.minsize(650, 650)
        root.configure(bg="#F5F7FB")

        self.game_name = tk.StringVar(value="Connect Four")
        self.stage = tk.StringVar(value="Early Game")
        self.iterations = tk.StringVar(value="40")
        self.depth = tk.StringVar(value="2")
        self.delay = tk.IntVar(value=350)
        self.status = tk.StringVar(value="Choose settings and press Start.")
        self.seed_text = tk.StringVar(value="10")

        self.game = None
        self.agents = {}
        self.running = False
        self.paused = False
        self.job = None
        self.generation = 0
        self.moves_played = 0

        self._build_ui()
        self.reset()

    def _build_ui(self):
        header = tk.Frame(self.root, bg="#192943", padx=18, pady=14)
        header.pack(fill="x")
        tk.Label(header, text="AI GAME ARENA", bg="#192943", fg="white",
                 font=("Arial", 19, "bold")).pack(anchor="w")
        tk.Label(header, text="Minimax (pink) vs MCTS (blue) | Demonstration only",
                 bg="#192943", fg="#C9D7EA", font=("Arial", 10)).pack(anchor="w")

        controls = ttk.Frame(self.root, padding=12)
        controls.pack(fill="x")
        fields = [
            ("Game", self.game_name, ["Connect Four", "Othello"]),
            ("Stage", self.stage, ["Early Game", "Endgame"]),
            ("MCTS iterations", self.iterations, ["20", "40", "120", "300", "500"]),
            ("Minimax depth", self.depth, ["1", "2", "3", "4"]),
        ]
        for i, (label, variable, values) in enumerate(fields):
            ttk.Label(controls, text=label).grid(row=0, column=i, sticky="w", padx=4)
            ttk.Combobox(controls, textvariable=variable, values=values,
                         width=16, state="readonly").grid(row=1, column=i, padx=4, pady=4)

        ttk.Label(controls, text="Opening seed").grid(row=2, column=0, sticky="w", padx=4)
        ttk.Entry(controls, textvariable=self.seed_text, width=12).grid(row=3, column=0, sticky="w", padx=4)
        ttk.Label(controls, text="Delay (ms)").grid(row=2, column=1, sticky="w", padx=4)
        ttk.Scale(controls, from_=100, to=1200, variable=self.delay,
                  orient="horizontal", length=140).grid(row=3, column=1, columnspan=2, sticky="w", padx=4)

        actions = ttk.Frame(self.root, padding=(12, 0, 12, 8))
        actions.pack(fill="x")
        ttk.Button(actions, text="Start", command=self.start).pack(side="left", padx=4)
        self.pause_button = ttk.Button(actions, text="Pause", command=self.toggle_pause)
        self.pause_button.pack(side="left", padx=4)
        ttk.Button(actions, text="Reset", command=self.reset).pack(side="left", padx=4)
        ttk.Label(self.root, textvariable=self.status, wraplength=790,
                  font=("Arial", 11), padding=(12, 4)).pack(fill="x")

        self.canvas = tk.Canvas(self.root, bg="white", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=18, pady=(5, 16))
        self.canvas.bind("<Configure>", lambda _event: self.draw_board())

    def _cancel_job(self):
        if self.job is not None:
            try:
                self.root.after_cancel(self.job)
            except tk.TclError:
                pass
            self.job = None

    def _new_game(self):
        return ConnectFour() if self.game_name.get() == "Connect Four" else Othello()

    def _prepare_endgame(self, seed):
        for attempt in range(500):
            rng = random.Random(seed + attempt)
            game = self._new_game()
            while game.check_winner() is None:
                if np.count_nonzero(game.board) / game.board.size >= 0.70:
                    return game
                moves = game.get_valid_moves()
                if moves:
                    game.make_move(rng.choice(moves))
                else:
                    game.make_move(None)  # Othello pass
        return None

    def reset(self):
        self.generation += 1
        self._cancel_job()
        self.running = False
        self.paused = False
        self.pause_button.configure(text="Pause")
        self.game = self._new_game()
        self.moves_played = 0
        self.agents = {}
        self.status.set("Ready. Pink = Minimax (X), blue = MCTS (O). Press Start.")
        self.draw_board()

    def start(self):
        if self.running:
            return
        try:
            seed = int(self.seed_text.get())
            iterations = int(self.iterations.get())
            depth = int(self.depth.get())
            if iterations < 1 or depth < 1:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid settings", "Use integer seed, iterations >= 1 and depth >= 1.")
            return

        self.generation += 1
        self._cancel_job()
        self.game = self._new_game()
        self.moves_played = 0
        if self.stage.get() == "Endgame":
            prepared = self._prepare_endgame(seed)
            if prepared is None:
                self.status.set("No nonterminal 70% position found. Try a different seed.")
                self.draw_board()
                return
            self.game = prepared

        self.agents = {
            1: ("Minimax", MinimaxAgent(max_depth=depth)),
            -1: ("MCTS", MCTSAgent(iterations=iterations, seed=seed)),
        }
        self.running = True
        self.paused = False
        self.pause_button.configure(text="Pause")
        self.draw_board()
        self._schedule(100)

    def toggle_pause(self):
        if not self.running:
            return
        self.paused = not self.paused
        self.pause_button.configure(text="Resume" if self.paused else "Pause")
        if self.paused:
            self._cancel_job()
            self.status.set("Paused.")
        else:
            self._schedule(50)

    def _schedule(self, delay):
        self._cancel_job()
        generation = self.generation
        self.job = self.root.after(delay, lambda: self._step(generation))

    def _step(self, generation):
        self.job = None
        if generation != self.generation or not self.running or self.paused:
            return
        winner = self.game.check_winner()
        if winner is not None:
            self._finish(winner)
            return
        player = self.game.current_player
        agent_name, agent = self.agents[player]
        move = agent.choose_move(copy.deepcopy(self.game))
        if not self.game.make_move(move):
            self.running = False
            messagebox.showerror("Invalid move", f"{agent_name} returned an illegal move: {move}")
            return
        self.moves_played += 1
        self.draw_board()
        winner = self.game.check_winner()
        if winner is not None:
            self._finish(winner)
        else:
            self.status.set(f"Move {self.moves_played}: {agent_name} played {move}. Next: {self.agents[self.game.current_player][0]}")
            self._schedule(int(self.delay.get()))

    def _finish(self, winner):
        self.running = False
        if winner == 0:
            result = "Draw"
        else:
            result = f"{self.agents[winner][0]} wins!"
        self.status.set(f"Game finished after {self.moves_played} displayed moves. {result}")
        self.draw_board()

    def draw_board(self):
        self.canvas.delete("all")
        if self.game is None:
            return
        board = self.game.board
        rows, cols = board.shape
        w = max(self.canvas.winfo_width(), 200)
        h = max(self.canvas.winfo_height(), 200)
        cell = min((w - 36) / cols, (h - 36) / rows)
        x0 = (w - cols * cell) / 2
        y0 = (h - rows * cell) / 2
        self.canvas.create_rectangle(x0, y0, x0 + cols * cell, y0 + rows * cell,
                                     fill="#2765AB" if cols == 7 else "#27865E", outline="")
        for r in range(rows):
            for c in range(cols):
                margin = cell * 0.13
                x = x0 + c * cell
                y = y0 + r * cell
                value = int(board[r, c])
                self.canvas.create_oval(x + margin, y + margin,
                                        x + cell - margin, y + cell - margin,
                                        fill=self.COLORS[value], outline="#163452", width=1)
        if cols == 8 and self.game.check_winner() is None:
            for r, c in self.game.get_valid_moves():
                x = x0 + (c + 0.5) * cell
                y = y0 + (r + 0.5) * cell
                radius = max(2, cell * 0.06)
                self.canvas.create_oval(x - radius, y - radius, x + radius, y + radius,
                                        fill="#FCE68A", outline="")


def main():
    root = tk.Tk()
    VisualArena(root)
    root.mainloop()


if __name__ == "__main__":
    main()
