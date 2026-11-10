import numpy as np

class ConnectFour:
    """Connect Four rules and board state for two players."""
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
        # Center column is highly valued in Connect 4
        score = 0
        center_array = self.board[:, 3]
        score += np.sum(center_array == 1) * 3
        score -= np.sum(center_array == -1) * 3
        return score
