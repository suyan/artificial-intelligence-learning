#!/usr/bin/python
import sys


class Board(object):
    int_min = -sys.maxint - 1
    int_max = sys.maxint

    def __init__(self, board, values, player, lastX = 0, lastY = 0):
        self.board = board
        self.values = values
        self.length = len(board)
        self.lastX = lastX
        self.lastY = lastY

        if player == 'X':
            self.player1 = 'X'
            self.player2 = 'O'
        if player == 'O':
            self.player1 = 'O'
            self.player2 = 'X'

        self.max_player = player
        self.evaluation = self.get_evaluation()

    # return False if invalid position
    def set_square(self, x, y):
        if (x < 0) or (x >= self.length) or (y < 0) or (y >= self.length):
            return False

        if self.board[x][y] == '*':
            if self.is_raid(x, y):
                self.do_raid(x, y)
            else:
                self.do_sneak(x, y)
            self.evaluation = self.get_evaluation()
            self.lastX = x
            self.lastY = y
            return True
        else:
            return False

    def is_raid(self, x, y):
        up = '*' if x - 1 < 0 else self.board[x - 1][y]
        down = '*' if x + 1 >= self.length else self.board[x + 1][y]
        left = '*' if y - 1 < 0 else self.board[x][y - 1]
        right = '*' if y + 1 >= self.length else self.board[x][y + 1]

        if (up == self.player1) or (down == self.player1) or (left == self.player1) or (right == self.player1):
            return True
        else:
            return False

    def do_raid(self, x, y):
        self.board[x][y] = self.player1
        up = '*' if x - 1 < 0 else self.board[x - 1][y]
        down = '*' if x + 1 >= self.length else self.board[x + 1][y]
        left = '*' if y - 1 < 0 else self.board[x][y - 1]
        right = '*' if y + 1 >= self.length else self.board[x][y + 1]

        if up == self.player2:
            self.board[x - 1][y] = self.player1
        if down == self.player2:
            self.board[x + 1][y] = self.player1
        if left == self.player2:
            self.board[x][y - 1] = self.player1
        if right == self.player2:
            self.board[x][y + 1] = self.player1

    def do_sneak(self, x, y):
        self.board[x][y] = self.player1

    def swap_player(self):
        self.player1, self.player2 = self.player2, self.player1

    def set_player(self, player):
        if player == 'X':
            self.player1 = 'X'
            self.player2 = 'O'
        else:
            self.player1 = 'O'
            self.player2 = 'X'

    def get_evaluation(self):
        evaluation = 0

        for i in range(0, self.length):
            for j in range(0, self.length):
                if self.board[i][j] == self.max_player:
                    evaluation += self.values[i][j]
                elif self.board[i][j] != "*":
                    evaluation -= self.values[i][j]

        return evaluation

    def get_evaluation_string(self):
        if self.evaluation == self.int_max:
            return "Infinity"
        if self.evaluation == self.int_min:
            return "-Infinity"
        return self.evaluation

    def set_evaluation(self, evaluation):
        self.evaluation = evaluation

    def get_board_string(self):
        board_string = ""
        for i in range(0, self.length):
            board_string += "".join(self.board[i]) + "\n"

        return board_string

    def __str__(self):
        output = "The state of board is:\n"
        for i in range(self.length):
            output += ' '.join(self.board[i]) + "\n"
        return output

    # make sure large value first in priority queue
    def __cmp__(self, other):
        if self.evaluation < other.evaluation:
            return 1
        elif self.evaluation > other.evaluation:
            return -1
        else:
            if self.lastX < other.lastX:
                return -1
            elif self.lastX > other.lastX:
                return 1
            else:
                if self.lastY < other.lastY:
                    return -1
                elif self.lastY > other.lastY:
                    return 1

        return 0
