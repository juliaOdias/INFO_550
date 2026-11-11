
import random
import copy
import math

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

    
    def order_moves(self, game, moves, player):
        scored_moves = []

        for move in moves:
            next_game = copy.deepcopy(game)
            next_game.make_move(move)

            winner = next_game.check_winner()

            if winner == player:
                score = 100000
            elif winner == -player:
                score = -100000
            elif winner == 0:
                score = 0
            else:
                score = next_game.evaluate_board() * player

            scored_moves.append((score, move))

        scored_moves.sort(
            key=lambda item: item[0],
            reverse=True
        )

        return [move for score, move in scored_moves]


    
    def choose_move(self, game):
        moves = game.get_valid_moves()

        if not moves:
            return None

        player = game.current_player
        moves = self.order_moves(game, moves, player)

        best_score = float("-inf")
        best_move = moves[0]

        alpha = float("-inf")
        beta = float("inf")

        for move in moves:
            next_game = copy.deepcopy(game)
            next_game.make_move(move)

            score = self.minimax(
                next_game,
                self.max_depth - 1,
                alpha,
                beta,
                player
            )

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

class MCTSNode:
    def __init__(self, game, parent=None, move=None):
        self.game = game
        self.parent = parent
        self.move = move
        self.children = []
        self.visits = 0
        self.wins = 0.0

        self.untried_moves = game.get_valid_moves()

        if not self.untried_moves and game.check_winner() is None:
            self.untried_moves = [None]

    def ucb1(self, exploration=1.414):
        if self.visits == 0:
            return float("inf")

        exploitation = self.wins / self.visits
        exploration_term = exploration * math.sqrt(
            math.log(self.parent.visits) / self.visits
        )

        return exploitation + exploration_term

class MCTSAgent:
    def __init__(self, iterations=100, seed=None):
        self.iterations = iterations
        self.rng = random.Random(seed)

    def choose_move(self, game):
        moves = game.get_valid_moves()

        if not moves:
            return None

        root = MCTSNode(copy.deepcopy(game))

        for _ in range(self.iterations):
            node = root

            while not node.untried_moves and node.children:
                node = max(
                    node.children,
                    key=lambda child: child.ucb1()
                )

            if node.untried_moves:
                move = self.rng.choice(node.untried_moves)
                node.untried_moves.remove(move)

                next_game = copy.deepcopy(node.game)
                next_game.make_move(move)

                child = MCTSNode(next_game, parent=node, move=move)
                node.children.append(child)
                node = child

            simulation = copy.deepcopy(node.game)

            while simulation.check_winner() is None:
                valid_moves = simulation.get_valid_moves()

                if valid_moves:
                    move = self.rng.choice(valid_moves)
                    simulation.make_move(move)
                else:
                    simulation.make_move(None)

            winner = simulation.check_winner()

            while node is not None:
                node.visits += 1
                previous_player = -node.game.current_player

                if winner == previous_player:
                    node.wins += 1
                elif winner == 0:
                    node.wins += 0.5

                node = node.parent

        best_child = max(
            root.children,
            key=lambda child: child.visits
        )

        return best_child.move