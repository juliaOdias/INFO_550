
from problems import ConnectFour, Othello
from algorithms import RandomAgent


def play_connect_four():
    game = ConnectFour()

    agents = {
        1: RandomAgent(seed=10),
        -1: RandomAgent(seed=20)
    }

    print("Connect Four: Random vs Random")

    while game.check_winner() is None:
        print()
        game.print_board()

        player = game.current_player
        move = agents[player].choose_move(game)

        if move is None:
            break

        print(f"Player {player} chooses column {move}")
        game.make_move(move)

    print("\nFinal Board:")
    game.print_board()

    winner = game.check_winner()

    if winner == 0:
        print("Result: Draw")
    elif winner is not None:
        print(f"Winner: Player {winner}")
    else:
        print("Game stopped before completion")

def play_game(game, game_name):
    agents = {
        1: RandomAgent(seed=10),
        -1: RandomAgent(seed=20)
    }

    print("\n=== " + game_name + ": Random vs Random ===")

    moves = 0
    max_moves = 100

    while game.check_winner() is None and moves < max_moves:
        player = game.current_player
        move = agents[player].choose_move(game)

        if move is None:
            if isinstance(game, Othello):
                print("Player", player, "passes")
                game.make_move(None)
                moves += 1
                continue
            break

        print("\nPlayer", player, "chooses", move)
        game.make_move(move)
        game.print_board()
        moves += 1

    print("\nFinal result for", game_name)

    winner = game.check_winner()

    if winner == 0:
        print("Draw")
    elif winner is None:
        print("Game stopped before completion")
    else:
        print("Winner: Player", winner)


if __name__ == "__main__":
    play_game(ConnectFour(), "Connect Four")
    play_game(Othello(), "Othello")