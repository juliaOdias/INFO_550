
import random
import copy

class RandomAgent:

    def __init__(self, seed=None):
        self.rng = random.Random(seed)

    def choose_move(self, game):
        valid_moves = game.get_valid_moves()

        if not valid_moves:
            return None

        return self.rng.choice(valid_moves)


class MinimaxAgent:
    def __init__(self, max_depth=3):
        self.max_depth = max_depth

    def choose_move(self, game):
        moves = game.get_valid_moves()

        if not moves:
            return None

        player = game.current_player
        best_score = float("-inf")
        best_move = moves[0]

        alpha = float("-inf")
        beta = float("inf")

        for move in moves:
            next_game = copy.deepcopy(game)
            next_game.make_move(move)

            score = self.minimax(next_game, self.max_depth - 1, alpha, beta, player)

            if score > best_score:
                best_score = score
                best_move = move

            alpha = max(alpha, best_score)

        return best_move

    def minimax(self, game, depth, alpha, beta, player):
        winner = game.check_winner()

        if winner is not None:
            if winner == player:
                return 100000 + depth
            if winner == -player:
                return -100000 - depth
            return 0

        if depth == 0:
            return game.evaluate_board() * player

        moves = game.get_valid_moves()

        if not moves:
            next_game = copy.deepcopy(game)
            next_game.make_move(None)

            return self.minimax(next_game, depth - 1, alpha, beta, player)

        maximizing = game.current_player == player

        if maximizing:
            best_score = float("-inf")

            for move in moves:
                next_game = copy.deepcopy(game)
                next_game.make_move(move)

                score = self.minimax( next_game, depth - 1, alpha, beta, player)

                best_score = max(best_score, score)
                alpha = max(alpha, best_score)

                if beta <= alpha:
                    break

            return best_score

        else:
            best_score = float("inf")

            for move in moves:
                next_game = copy.deepcopy(game)
                next_game.make_move(move)

                score = self.minimax(next_game, depth - 1, alpha, beta, player)

                best_score = min(best_score, score)
                beta = min(beta, best_score)

                if beta <= alpha:
                    break

            return best_score
