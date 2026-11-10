import csv
import random
import copy
import numpy as np
import matplotlib.pyplot as plt
from problems import ConnectFour, Othello
from algorithms import MinimaxAgent, MCTSAgent


def play_match(game, minimax_first=True, seed=10):
    game = copy.deepcopy(game)

    agents = {
        1: MinimaxAgent(max_depth=2) if minimax_first
           else MCTSAgent(iterations=40, seed=seed),
        -1: MCTSAgent(iterations=40, seed=seed)
            if minimax_first else MinimaxAgent(max_depth=2)
    }

    while game.check_winner() is None:
        player = game.current_player
        move = agents[player].choose_move(game)

        if move is None:
            if not isinstance(game, Othello):
                raise RuntimeError("Unexpected missing move")
            if not game.make_move(None):
                raise RuntimeError("Invalid pass")
        else:
            if not game.make_move(move):
                raise RuntimeError("Invalid move")

    winner = game.check_winner()

    if winner == 0:
        return "Draw"

    minimax_player = 1 if minimax_first else -1
    return "Minimax" if winner == minimax_player else "MCTS"

def random_position(game_class, target, seed):
    rng = random.Random(seed)
    game = game_class()

    total_cells = game.board.size

    while game.check_winner() is None:
        occupied = np.count_nonzero(game.board)
        occupancy = occupied / total_cells

        if occupancy >= target:
            return game, occupancy

        moves = game.get_valid_moves()

        if moves:
            game.make_move(rng.choice(moves))
        else:
            game.make_move(None)

    return None, None


def generate_positions(game_class, stage, count=2):
    target = 0.20 if stage == "Early" else 0.70
    positions = []
    seen = set()

    for attempt in range(2000):
        if len(positions) == count:
            break

        game, occupancy = random_position(
            game_class,
            target,
            seed=1000 + attempt
        )

        if game is None:
            continue

        key = (game.board.tobytes(), game.current_player)

        if key in seen:
            continue

        seen.add(key)
        positions.append((game, occupancy))

    return positions


def run_experiments():
    rows = []

    games = [
        (ConnectFour, "Connect Four"),
        (Othello, "Othello")
    ]

    for game_class, game_name in games:
        for stage in ["Early", "Endgame"]:
            positions = generate_positions(
                game_class, stage, count=2
            )

            if not positions:
                print(
                    "No qualifying positions:",
                    game_name, stage
                )
                continue

            print(
                "\n", game_name, stage,
                "| Positions:", len(positions),
                flush=True
            )

            for position_id, (game, occupancy) in enumerate(
                positions, start=1
            ):
                for minimax_first in [True, False]:
                    seed = (
                        5000 + position_id
                        + (0 if minimax_first else 100)
                    )

                    winner = play_match(
                        game,
                        minimax_first=minimax_first,
                        seed=seed
                    )

                    row = {
                        "game": game_name,
                        "stage": stage,
                        "position": position_id,
                        "occupancy": round(float(occupancy), 3),
                        "minimax_player": (
                            1 if minimax_first else -1
                        ),
                        "winner": winner
                    }

                    rows.append(row)
                    print(row, flush=True)

    return rows


def save_results(rows):
    if not rows:
        print("No results to save")
        return

    with open(
        "experiment_results.csv",
        "w",
        newline="",
        encoding="utf-8"
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=list(rows[0].keys())
        )
        writer.writeheader()
        writer.writerows(rows)

    print("\nSaved experiment_results.csv")


def plot_results(rows):
    if not rows:
        return

    labels = []
    minimax_wins = []
    mcts_wins = []
    draws = []

    for game in ["Connect Four", "Othello"]:
        for stage in ["Early", "Endgame"]:
            subset = [
                row for row in rows
                if row["game"] == game
                and row["stage"] == stage
            ]

            if not subset:
                continue

            labels.append(game + "\n" + stage)
            minimax_wins.append(
                sum(r["winner"] == "Minimax" for r in subset)
            )
            mcts_wins.append(
                sum(r["winner"] == "MCTS" for r in subset)
            )
            draws.append(
                sum(r["winner"] == "Draw" for r in subset)
            )

    x = np.arange(len(labels))
    width = 0.25

    plt.figure(figsize=(10, 5))
    plt.bar(x - width, minimax_wins, width, label="Minimax")
    plt.bar(x, mcts_wins, width, label="MCTS")
    plt.bar(x + width, draws, width, label="Draw")

    plt.xticks(x, labels)
    plt.ylabel("Number of games")
    plt.title("Minimax vs MCTS by Game Stage")
    plt.legend()
    plt.tight_layout()

    plt.savefig("experiment_results.png", dpi=150)
    plt.close()

    print("Saved experiment_results.png")


if __name__ == "__main__":
    results = run_experiments()
    save_results(results)
    plot_results(results)