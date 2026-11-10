
import random


class RandomAgent:

    def __init__(self, seed=None):
        self.rng = random.Random(seed)

    def choose_move(self, game):
        valid_moves = game.get_valid_moves()

        if not valid_moves:
            return None

        return self.rng.choice(valid_moves)
