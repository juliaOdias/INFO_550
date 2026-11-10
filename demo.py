
from problems import ConnectFour
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


if __name__ == "__main__":
    play_connect_four()