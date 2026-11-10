
from problems import ConnectFour, Othello
from algorithms import MinimaxAgent, MCTSAgent


def play_match(game_class, minimax_first=True):
    game = game_class()

    minimax = MinimaxAgent(max_depth=2)
    mcts = MCTSAgent(iterations=40, seed=10)

    if minimax_first:
        agents = {1: minimax, -1: mcts}
    else:
        agents = {1: mcts, -1: minimax}

    while game.check_winner() is None:
        player = game.current_player
        move = agents[player].choose_move(game)

        if move is None:
            if isinstance(game, Othello):
                if not game.make_move(None):
                    raise RuntimeError("Invalid pass")
                continue

            raise RuntimeError("No legal move in active game")

        if not game.make_move(move):
            raise RuntimeError("Agent selected an invalid move")

    winner = game.check_winner()

    if winner == 0:
        return "Draw"

    if winner == (1 if minimax_first else -1):
        return "Minimax"

    return "MCTS"


def compare_agents(game_class, game_name, num_games=4):
    results = {
        "Minimax": 0,
        "MCTS": 0,
        "Draw": 0
    }

    print("\n=== " + game_name + " ===")

    for i in range(num_games):
        minimax_first = (i % 2 == 0)

        winner = play_match(game_class, minimax_first)
        results[winner] += 1

        print(
            "Game", i + 1,
            "| First:", "Minimax" if minimax_first else "MCTS",
            "| Result:", winner
        )

    print("\nResults:")
    print("Minimax wins:", results["Minimax"])
    print("MCTS wins:", results["MCTS"])
    print("Draws:", results["Draw"])

    return results


if __name__ == "__main__":
    compare_agents(ConnectFour, "Connect Four")
    compare_agents(Othello, "Othello")
