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
        score = 0
        center_array = self.board[:, 3]
        score += np.sum(center_array == 1) * 3
        score -= np.sum(center_array == -1) * 3
        return score


class Othello:
    def __init__(self):
        self.board = np.zeros((8, 8), dtype=int)
        self.current_player = 1

        # Starting pieces
        self.board[3, 3] = -1
        self.board[3, 4] = 1
        self.board[4, 3] = 1
        self.board[4, 4] = -1

        # Directions to check around a piece
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
        # The game ends when neither player can move
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
        # Basic evaluation using piece difference
        return int(
            np.sum(self.board == 1) -
            np.sum(self.board == -1)
        )
