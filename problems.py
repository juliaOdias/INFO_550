import numpy as np

class ConnectFour:
    def __init__(self):
        self.board = np.zeros((6, 7), dtype=int)
        self.current_player = 1

    def get_valid_moves(self):
        valid_moves = []
        for col in range(7):
            if self.board[0, col] == 0:
                valid_moves.append(col)
        return valid_moves

    def make_move(self, col):
        if col not in self.get_valid_moves(): return False
        for row in range(5, -1, -1):
            if self.board[row, col] == 0:
                self.board[row, col] = self.current_player
                self.current_player *= -1 
                return True
        return False

    def check_winner(self):
        for c in range(4):
            for r in range(6):
                if self.board[r,c] == self.board[r,c+1] == self.board[r,c+2] == self.board[r,c+3] != 0: return self.board[r,c]
        for c in range(7):
            for r in range(3):
                if self.board[r,c] == self.board[r+1,c] == self.board[r+2,c] == self.board[r+3,c] != 0: return self.board[r,c]
        for c in range(4):
            for r in range(3, 6):
                if self.board[r,c] == self.board[r-1,c+1] == self.board[r-2,c+2] == self.board[r-3,c+3] != 0: return self.board[r,c]
        for c in range(4):
            for r in range(3):
                if self.board[r,c] == self.board[r+1,c+1] == self.board[r+2,c+2] == self.board[r+3,c+3] != 0: return self.board[r,c]
        if len(self.get_valid_moves()) == 0: return 0 
        return None

    def print_board(self):
        symbols = {1: 'X', -1: 'O', 0: '.'}
        print("0 1 2 3 4 5 6")
        for row in self.board:
            print(" ".join([symbols[x] for x in row]))
        print("-------------")

    
    def evaluate_board(self):
        def score_window(window, player):
            own = window.count(player)
            opponent = window.count(-player)
            empty = window.count(0)

            if own == 4:
                return 1000
            if opponent == 4:
                return -1000
            if own == 3 and empty == 1:
                return 50
            if opponent == 3 and empty == 1:
                return -80
            if own == 2 and empty == 2:
                return 10
            if opponent == 2 and empty == 2:
                return -10
            return 0

        def evaluate_player(player):
            score = 0

            # Center column control
            center = list(self.board[:, 3])
            score += center.count(player) * 6
            for row in range(6):
                for col in range(4):
                    window = list(self.board[row, col:col + 4])
                    score += score_window(window, player)
            for row in range(3):
                for col in range(7):
                    window = list(self.board[row:row + 4, col])
                    score += score_window(window, player)
            for row in range(3):
                for col in range(4):
                    window = [
                        self.board[row + i, col + i]
                        for i in range(4)
                    ]
                    score += score_window(window, player)
            for row in range(3, 6):
                for col in range(4):
                    window = [
                        self.board[row - i, col + i]
                        for i in range(4)
                    ]
                    score += score_window(window, player)

            return score

        return (
            evaluate_player(1) -
            evaluate_player(-1)
        ) / 2


class Othello:
    def __init__(self):
        self.board = np.zeros((8, 8), dtype=int)
        self.current_player = 1

        self.board[3, 3] = -1
        self.board[3, 4] = 1
        self.board[4, 3] = 1
        self.board[4, 4] = -1

        self.directions = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1),           (0, 1),
            (1, -1),  (1, 0),  (1, 1)
        ]

    def get_flips(self, row, col, player):
        if self.board[row, col] != 0:
            return []

        flips = []

        for dr, dc in self.directions:
            r = row + dr
            c = col + dc
            found = []

            while 0 <= r < 8 and 0 <= c < 8:
                if self.board[r, c] == -player:
                    found.append((r, c))
                elif self.board[r, c] == player:
                    if found:
                        flips.extend(found)
                    break
                else:
                    break

                r += dr
                c += dc

        return flips

    def get_valid_moves(self, player=None):
        if player is None:
            player = self.current_player

        moves = []

        for row in range(8):
            for col in range(8):
                if self.get_flips(row, col, player):
                    moves.append((row, col))

        return moves

    def make_move(self, move):
        if move is None:
            if self.get_valid_moves():
                return False

            self.current_player *= -1
            return True

        if move not in self.get_valid_moves():
            return False

        row, col = move
        flips = self.get_flips(row, col, self.current_player)

        self.board[row, col] = self.current_player

        for r, c in flips:
            self.board[r, c] = self.current_player

        self.current_player *= -1
        return True

    def check_winner(self):
        if self.get_valid_moves(1) or self.get_valid_moves(-1):
            return None

        black = np.sum(self.board == 1)
        white = np.sum(self.board == -1)

        if black > white:
            return 1
        elif white > black:
            return -1
        return 0

    def print_board(self):
        symbols = {1: "X", -1: "O", 0: "."}

        print("  0 1 2 3 4 5 6 7")

        for row in range(8):
            cells = [
                symbols[self.board[row, col]]
                for col in range(8)
            ]
            print(row, " ".join(cells))

        print("X:", np.sum(self.board == 1),
              "O:", np.sum(self.board == -1))

    
    def evaluate_board(self):
        weights = np.array([
            [100, -20, 10,  5,  5, 10, -20, 100],
            [-20, -50, -2, -2, -2, -2, -50, -20],
            [ 10,  -2,  5,  1,  1,  5,  -2,  10],
            [  5,  -2,  1,  0,  0,  1,  -2,   5],
            [  5,  -2,  1,  0,  0,  1,  -2,   5],
            [ 10,  -2,  5,  1,  1,  5,  -2,  10],
            [-20, -50, -2, -2, -2, -2, -50, -20],
            [100, -20, 10,  5,  5, 10, -20, 100]
        ])

        positional_score = np.sum(self.board * weights)

        piece_score = (
            np.sum(self.board == 1) -
            np.sum(self.board == -1)
        )

        return float(positional_score + piece_score)
