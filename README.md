
# Adversarial Search Algorithms: Minimax and MCTS

This Python project investigates whether the relative performance of Minimax and Monte Carlo Tree Search (MCTS) changes between Early Game and Endgame. The games are Othello (Reversi) and Connect Four. The project compares both algorithms using different search depths, MCTS iterations, and starting game positions.

## Hypotheses and experiments

1. **Early Game performance:** Does MCTS perform better than Minimax during the early stages of a game? Both algorithms are evaluated from the same starting positions, with player assignments swapped.

2. **Endgame performance:** Does Minimax perform better than MCTS during the later stages of a game? Nonterminal positions are generated through seeded random legal moves until approximately 70% board occupancy. Both algorithms are evaluated from the same starting positions, with player assignments swapped.

3. **Search parameters:** How do Minimax search depth and MCTS iterations affect performance? The experiments compare Minimax depths of **2, 3, and 4** against MCTS with **40, 120, 300, and 500 iterations**.

The completed experiment includes **192 matches** across both games and stages, using two starting positions per game and stage.

Score: win = 1, draw = 0.5, loss = 0. The experiments record winners, decision times, random seeds, search parameters, and starting occupancy. Results are saved as CSV files and Matplotlib PNG charts.

**Preliminary results:**
- **Connect Four Early Game:** Minimax 41 wins, MCTS 5 wins, 2 draws.
- **Connect Four Endgame:** Minimax 24 wins, MCTS 24 wins.
- **Othello Early Game:** Minimax 9 wins, MCTS 37 wins, 2 draws.
- **Othello Endgame:** Minimax 21 wins, MCTS 27 wins.

**Caveat:** The 20% and 70% occupancy thresholds are operational definitions of Early Game and Endgame, not necessarily true strategic stages. Connect Four games may terminate before reaching 70% occupancy, so only qualifying nonterminal positions are used. The results are preliminary because only two unique starting positions were evaluated per game and stage.

## Algorithms

- **Minimax:** Depth-limited search with Alpha-Beta Pruning and Move Ordering. Configurable depths of 2, 3, and 4. The Connect Four evaluation function considers center control and potential winning sequences. The Othello evaluation function uses positional weights and piece differences.

- **MCTS:** UCB1 selection, expansion, random rollouts, and backpropagation. Configurable iterations of 40, 120, 300, and 500 per move.

- **RandomAgent:** Selects random legal moves using a configurable seed. Used for baseline demonstrations and reproducible starting-position generation.

## How to run

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Run the basic Random vs Random demonstration:

```bash
python demo.py
```

Run Minimax vs MCTS experiments:

```bash
python comparisons.py --positions 2 --depths 2 3 4 --iterations 40 120 300 500
```

Launch the optional Tkinter interface:

```bash
python visual_arena.py
```

The experiments run independently of the graphical interface.

Results are saved to `parameter_results.csv`, and charts to `parameter_results.png`.

## Project structure

- `problems.py`: NumPy implementations of Connect Four and Othello, including game rules, valid moves, and terminal states.
- `algorithms.py`: RandomAgent, Minimax with Alpha-Beta Pruning and Move Ordering, and MCTS with UCB1.
- `comparisons.py`: Early Game and Endgame experiments, parameter comparisons, execution-time measurements, CSV results, and charts.
- `demo.py`: Random vs Random terminal demonstrations for both games.
- `visual_arena.py`: Optional Tkinter AI vs AI demonstration.
- `requirements.txt`: Python dependencies.
- `parameter_results.csv`: Experimental results from 192 matches.
- `parameter_results.png`: Matplotlib visualization of the results.

**Author:** Julia Dias — University of Arizona, Artificial Intelligence Project
