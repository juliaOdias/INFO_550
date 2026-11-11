import csv
import random
import copy
import argparse
import time
import numpy as np
import matplotlib.pyplot as plt
from problems import ConnectFour, Othello
from algorithms import MinimaxAgent, MCTSAgent
from pathlib import Path


def play_match(game, minimax_first=True, seed=10,
               depth=2, iterations=40):
    game = copy.deepcopy(game)

    minimax_player = 1 if minimax_first else -1

    agents = {
        minimax_player: MinimaxAgent(max_depth=depth),
        -minimax_player: MCTSAgent(
            iterations=iterations, seed=seed
        )
    }

    minimax_time = 0.0
    mcts_time = 0.0
    moves_count = 0

    while game.check_winner() is None:
        player = game.current_player

        start = time.perf_counter()
        move = agents[player].choose_move(game)
        elapsed = time.perf_counter() - start

        if player == minimax_player:
            minimax_time += elapsed
        else:
            mcts_time += elapsed

        if move is None:
            if not isinstance(game, Othello):
                raise RuntimeError("Unexpected missing move")
            if not game.make_move(None):
                raise RuntimeError("Invalid pass")
        else:
            if not game.make_move(move):
                raise RuntimeError("Invalid move")

        moves_count += 1

        if moves_count > 200:
            raise RuntimeError("Game exceeded move limit")

    winner = game.check_winner()

    if winner == 0:
        result = "Draw"
    elif winner == minimax_player:
        result = "Minimax"
    else:
        result = "MCTS"

    return result, minimax_time, mcts_time, moves_count

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

def run_experiments(positions_count=2,
                    depths=None,
                    iterations_list=None):

    if depths is None:
        depths = [2, 3, 4]

    if iterations_list is None:
        iterations_list = [40, 120, 300, 500]

    output = Path("parameter_results.csv")

    fields = [
        "game", "stage", "position", "occupancy",
        "depth", "iterations", "minimax_player",
        "seed", "winner", "minimax_time",
        "mcts_time", "moves_count"
    ]

    rows = []

    if output.exists() and output.stat().st_size > 0:
        with output.open("r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)

            if reader.fieldnames != fields:
                raise ValueError(
                    "Existing CSV has different columns. "
                    "Rename it before running."
                )

            rows = list(reader)

    completed = {
        (
            r["game"], r["stage"],
            int(r["position"]), int(r["depth"]),
            int(r["iterations"]), int(r["minimax_player"])
        )
        for r in rows
    }

    games = [
        (ConnectFour, "Connect Four"),
        (Othello, "Othello")
    ]

    with output.open("a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fields)

        if output.stat().st_size == 0:
            writer.writeheader()
            file.flush()

        for game_index, (game_class, game_name) in enumerate(games):
            for stage_index, stage in enumerate(["Early", "Endgame"]):

                positions = generate_positions(game_class, stage, count=positions_count)

                print("\n", game_name, stage,"| Positions:", len(positions),flush=True)

                if len(positions) < positions_count:
                    print("WARNING: Fewer valid positions ""than requested.",flush=True)

                for position_id, (game, occupancy) in enumerate(positions, start=1):
                    for depth in depths:
                        for iterations in iterations_list:
                            for minimax_first in [True, False]:
                                minimax_player = (1 if minimax_first else -1)
                                key = (game_name, stage, position_id,depth, iterations, minimax_player)

                                if key in completed:
                                    continue

                                seed = (
                                    500000
                                    + game_index * 1000000
                                    + stage_index * 100000
                                    + position_id * 10000
                                    + depth * 1000
                                    + iterations * 2
                                    + (0 if minimax_first else 1)
                                )

                                winner, mm_time, mc_time, moves = play_match(
                                    game,
                                    minimax_first=minimax_first,
                                    seed=seed,
                                    depth=depth,
                                    iterations=iterations
                                )

                                row = {
                                    "game": game_name,
                                    "stage": stage,
                                    "position": position_id,
                                    "occupancy": round(
                                        float(occupancy), 3
                                    ),
                                    "depth": depth,
                                    "iterations": iterations,
                                    "minimax_player": minimax_player,
                                    "seed": seed,
                                    "winner": winner,
                                    "minimax_time": round(mm_time, 4),
                                    "mcts_time": round(mc_time, 4),
                                    "moves_count": moves
                                }

                                writer.writerow(row)
                                file.flush()

                                rows.append(row)
                                completed.add(key)

                                print(
                                    f"{game_name} | {stage} | "
                                    f"Position {position_id} | "
                                    f"Depth {depth} | "
                                    f"MCTS {iterations} | "
                                    f"MM player {minimax_player} | "
                                    f"Winner: {winner} | "
                                    f"MM time: {mm_time:.2f}s | "
                                    f"MCTS time: {mc_time:.2f}s",
                                    flush=True
                                )

    return rows

def plot_results(rows):
    if not rows:
        return

    categories = sorted({
        (r["game"],r["stage"],int(r["depth"]),int(r["iterations"]))
        for r in rows
    })

    labels = []
    minimax_wins = []
    mcts_wins = []
    draws = []

    for game, stage, depth, iterations in categories:
        subset = [
            r for r in rows
            if r["game"] == game
            and r["stage"] == stage
            and int(r["depth"]) == depth
            and int(r["iterations"]) == iterations
        ]

        short_game = "CF" if game == "Connect Four" else "OT"

        labels.append(f"{short_game} {stage[0]}\n"f"D{depth}/I{iterations}")

        minimax_wins.append(sum(r["winner"] == "Minimax" for r in subset))
        mcts_wins.append(sum(r["winner"] == "MCTS" for r in subset))
        draws.append(sum(r["winner"] == "Draw" for r in subset))

    x = np.arange(len(labels))
    width = 0.25

    plt.figure(figsize=(max(12, len(labels) * 0.5), 7))

    plt.bar(x - width, minimax_wins,width, label="Minimax")
    plt.bar(x, mcts_wins,width, label="MCTS")
    plt.bar(x + width, draws,width, label="Draw")

    plt.xticks(x, labels, rotation=70, ha="right")
    plt.ylabel("Number of games")
    plt.title("Minimax vs MCTS by Game Stage and Parameters")
    plt.legend()
    plt.tight_layout()

    plt.savefig("parameter_results.png", dpi=150)
    plt.close()

    print("Saved parameter_results.png")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Minimax vs MCTS experiments")

    parser.add_argument("--positions", type=int, default=2)
    parser.add_argument("--depths", type=int, nargs="+",default=[2, 3, 4])
    parser.add_argument("--iterations", type=int, nargs="+",default=[40, 120, 300, 500])
    args = parser.parse_args()

    if (args.positions < 1
        or any(d < 1 for d in args.depths)
        or any(i < 1 for i in args.iterations)
    ):
        parser.error("All parameters must be positive integers")

    results = run_experiments(positions_count=args.positions,depths=args.depths,iterations_list=args.iterations)

    plot_results(results)
