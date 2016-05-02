#!/usr/bin/python

import sys
import getopt
import copy
from heapq import *


class Solution(object):
    board_size = 5
    GBFS = 1
    MINIMAX = 2
    ALPHA_BETA_PRUNING = 3
    BATTLE = 4

    def __init__(self):
        self.input_file = Solution.get_input_file()
        parameters = Solution.get_input_parameters(self.input_file)
        self.board = parameters["board"]

        # greedy best first search = 1
        # MiniMax = 2
        # Alpha-beta Pruning = 3
        # Battle = 4
        self.task_num = int(parameters["task_num"])

        if self.task_num == Solution.GBFS:
            self.depth = parameters["depth"]
            self.run_greedy_best_first_search()
        elif self.task_num == Solution.MINIMAX:
            self.depth = parameters["depth"]
            self.run_minimax()
        elif self.task_num == Solution.ALPHA_BETA_PRUNING:
            self.depth = parameters["depth"]
            self.run_alpha_beta()
        elif self.task_num == self.BATTLE:
            self.depth1 = parameters["depth1"]
            self.depth2 = parameters["depth2"]
            self.task1 = parameters["task1"]
            self.task2 = parameters["task2"]
            self.player1 = parameters["player1"]
            self.player2 = parameters["player2"]
            self.run_battle()

    def run_greedy_best_first_search(self):
        agent = GreedyBestFirstSearch(self.board)
        board = agent.get_next_board()
        agent.output_next_state(board)

    def run_minimax(self):
        agent = MiniMax(self.board, self.depth)
        board = agent.get_next_board()
        agent.output_next_state(board)
        agent.output_log()

    def run_alpha_beta(self):
        agent = AlphaBetaPruning(self.board, self.depth)
        board = agent.get_next_board()
        agent.output_next_state(board)
        agent.output_log()

    def get_agent(self, task_id, board, depth):
        if task_id == self.GBFS:
            return GreedyBestFirstSearch(board)
        elif task_id == self.MINIMAX:
            return MiniMax(board, depth)
        else:
            return AlphaBetaPruning(board, depth)

    def run_battle(self):
        board = copy.deepcopy(self.board)
        wfile = open("./trace_state.txt", "w")
        while self.not_finished(board.board):
            if board.player1 == self.player1:
                board.max_player = self.player1
                agent = self.get_agent(self.task1, board, self.depth1)
            else:
                board.max_player = self.player2
                agent = self.get_agent(self.task2, board, self.depth2)
            board = agent.get_next_board()
            board.swap_player()
            wfile.write(board.get_board_string())

    def not_finished(self, board):
        for i in range(0, self.board_size):
            for j in range(0, self.board_size):
                if board[i][j] == "*":
                    return True
        return False

    @staticmethod
    def get_input_parameters(input_file):
        parameters = {}
        rfile = open(input_file)
        # read task num
        parameters["task_num"] = int(rfile.readline().strip())
        if parameters["task_num"] < 4:
            player1 = rfile.readline().strip()

            parameters["depth"] = rfile.readline().strip()

            board = list()
            values = list()
            # read board values
            for i in range(Solution.board_size):
                values.append([])
                for value in rfile.readline().split():
                    values[i].append(int(value))

            # read current state
            for i in range(Solution.board_size):
                board.append(list(rfile.readline().strip()))

            parameters["board"] = Board(board, values, player1)
        else:
            player1 = rfile.readline().strip()
            task1 = int(rfile.readline().strip())
            depth1 = int(rfile.readline().strip())
            player2 = rfile.readline().strip()
            task2 = int(rfile.readline().strip())
            depth2 = int(rfile.readline().strip())

            board = list()
            values = list()
            # read board values
            for i in range(Solution.board_size):
                values.append([])
                for value in rfile.readline().split():
                    values[i].append(int(value))

            # read current state
            for i in range(Solution.board_size):
                board.append(list(rfile.readline().strip()))

            parameters["board"] = Board(board, values, player1)
            parameters["depth1"] = depth1
            parameters["depth2"] = depth2
            parameters["task1"] = task1
            parameters["task2"] = task2
            parameters["player1"] = player1
            parameters["player2"] = player2

        return parameters

    @staticmethod
    def get_input_file():
        opts, args = getopt.getopt(sys.argv[1:], "i:")
        if len(opts) != 0:
            return opts[0][1]
        else:
            return "./input.txt"

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


class GreedyBestFirstSearch(object):

    def __init__(self, board):
        self.board = board

    def get_next_board(self):
        heap = []

        # push all next boards in priority queue
        for i in range(0, self.board.length):
            for j in range(0, self.board.length):
                new_board = copy.deepcopy(self.board)
                if new_board.set_square(i, j):
                    heappush(heap, new_board)

        # get best one from boards
        target = heappop(heap)
        target.set_player(self.board.player1)

        return target

    @staticmethod
    def output_next_state(board):
        output_filename = './next_state.txt'
        wfile = open(output_filename, "w")
        for i in range(0, len(board.board)):
            if i == len(board.board) - 1:
                wfile.write("".join(board.board[i]))
            else:
                wfile.write("".join(board.board[i]) + "\n")

class MiniMax(object):
    int_min = -sys.maxint - 1
    int_max = sys.maxint
    traverse_log = list()

    def __init__(self, board, max_depth):
        self.board = board
        self.board.set_evaluation(MiniMax.int_min)
        self.max_depth = int(max_depth)
        self.max_player = board.player1
        self.traverse_log.append("Node,Depth,Value")

    def get_next_board(self):
        board = self.minimax(self.board, 0, self.max_player)
        board.set_player(self.board.player1)
        return board

    @staticmethod
    def output_next_state(board):
        output_filename = './next_state.txt'
        wfile = open(output_filename, "w")
        for i in range(0, len(board.board)):
            if i == len(board.board) - 1:
                wfile.write("".join(board.board[i]))
            else:
                wfile.write("".join(board.board[i]) + "\n")

    def print_log(self, board, depth, evaluation):
        if evaluation == MiniMax.int_min:
            evaluation = "-Infinity"
        elif evaluation == MiniMax.int_max:
            evaluation = "Infinity"

        y_map = {0: "A", 1: "B", 2: "C", 3: "D", 4: "E"}
        x_map = {0: "1", 1: "2", 2: "3", 3: "4", 4: "5"}

        if depth == 0:
            self.traverse_log.append('root,0,%s' % evaluation)
        else:
            self.traverse_log.append('%s%s,%s,%s' % (y_map[board.lastY], x_map[board.lastX], depth, evaluation))

    def output_log(self):
        wfile = open("./traverse_log.txt", "w")
        for i in range(0, len(self.traverse_log)):
            if i == len(self.traverse_log) - 1:
                wfile.write(self.traverse_log[i])
            else:
                wfile.write(self.traverse_log[i] + "\n")

    def minimax(self, board, depth, current_player):
        # if touch leaf, return current board's evaluation
        if depth == self.max_depth:
            self.print_log(board, depth, board.evaluation)
            return board

        if current_player != board.player1:
            board.swap_player()

        if current_player == self.max_player:
            best_evaluation = MiniMax.int_min
            best_board = board
            self.print_log(best_board, depth, best_evaluation)

            for i in range(0, self.board.length):
                for j in range(0, self.board.length):
                    new_board = copy.deepcopy(board)
                    if new_board.set_square(i, j):
                        current_board = self.minimax(new_board, depth + 1, new_board.player2)
                        if current_board.evaluation > best_evaluation:
                            self.print_log(board, depth, current_board.evaluation)
                            best_evaluation = current_board.evaluation
                            best_board = new_board
                        else:
                            self.print_log(board, depth, best_evaluation)

            return best_board
        else:
            best_evaluation = MiniMax.int_max
            best_board = board
            self.print_log(best_board, depth, best_evaluation)

            for i in range(0, self.board.length):
                for j in range(0, self.board.length):
                    new_board = copy.deepcopy(board)
                    if new_board.set_square(i, j):
                        current_board = self.minimax(new_board, depth + 1, new_board.player2)
                        if current_board.evaluation < best_evaluation:
                            # update best board to current board
                            self.print_log(board, depth, current_board.evaluation)
                            best_evaluation = current_board.evaluation
                            best_board = current_board
                        else:
                            self.print_log(board, depth, best_evaluation)

            return best_board


class AlphaBetaPruning(object):
    int_min = -sys.maxint - 1
    int_max = sys.maxint
    traverse_log = list()

    def __init__(self, board, max_depth):
        self.board = board
        self.board.set_evaluation(AlphaBetaPruning.int_min)
        self.max_depth = int(max_depth)
        self.max_player = board.player1
        self.traverse_log.append("Node,Depth,Value,Alpha,Beta")

    def print_log(self, board, depth, evaluation, alpha, beta):
        evaluation = self.max_to_string(evaluation)
        alpha = self.max_to_string(alpha)
        beta = self.max_to_string(beta)

        y_map = {0: "A", 1: "B", 2: "C", 3: "D", 4: "E"}
        x_map = {0: "1", 1: "2", 2: "3", 3: "4", 4: "5"}

        if depth == 0:
            self.traverse_log.append('root,0,%s,%s,%s' % (evaluation, alpha, beta))
        else:
            self.traverse_log.append('%s%s,%s,%s,%s,%s' % (y_map[board.lastY], x_map[board.lastX], depth, evaluation, alpha, beta))

    @staticmethod
    def output_next_state(board):
        output_filename = './next_state.txt'
        wfile = open(output_filename, "w")
        for i in range(0, len(board.board)):
            if i == len(board.board) - 1:
                wfile.write("".join(board.board[i]))
            else:
                wfile.write("".join(board.board[i]) + "\n")

    def output_log(self):
        wfile = open("./traverse_log.txt", "w")
        for i in range(0, len(self.traverse_log)):
            if i == len(self.traverse_log) - 1:
                wfile.write(self.traverse_log[i])
            else:
                wfile.write(self.traverse_log[i] + "\n")

    def max_to_string(self, value):
        if value == self.int_min:
            return "-Infinity"
        if value == self.int_max:
            return "Infinity"
        return value

    def get_next_board(self):
        board = self.alphabeta(self.board, 0, self.int_min, self.int_max, self.max_player)
        board.set_player(self.board.player1)
        return board

    def alphabeta(self, board, depth, alpha, beta, current_player):
        # touch the leaf, return board
        if depth == self.max_depth:
            self.print_log(board, depth, board.evaluation, alpha, beta)
            return board

        if current_player != board.player1:
            board.swap_player()

        if current_player == self.max_player:
            best_evaluation = self.int_min
            best_board = board
            self.print_log(board, depth, best_evaluation, alpha, beta)

            for i in range(0, self.board.length):
                for j in range(0, self.board.length):
                    new_board = copy.deepcopy(board)
                    if new_board.set_square(i, j):
                        current_board = self.alphabeta(new_board, depth + 1, alpha, beta, new_board.player2)
                        if current_board.evaluation > best_evaluation:
                            best_evaluation = current_board.evaluation
                            best_board = new_board

                            if best_evaluation >= beta:
                                self.print_log(board, depth, current_board.evaluation, alpha, beta)
                                return best_board

                            if best_evaluation > alpha:
                                alpha = best_evaluation

                            self.print_log(board, depth, current_board.evaluation, alpha, beta)
                        else:
                            self.print_log(board, depth, best_evaluation, alpha, beta)

            return best_board
        else:
            best_evaluation = self.int_max
            best_board = board
            self.print_log(board, depth, best_evaluation, alpha, beta)
            for i in range(0, self.board.length):
                for j in range(0, self.board.length):
                    new_board = copy.deepcopy(board)
                    if new_board.set_square(i, j):
                        current_board = self.alphabeta(new_board, depth + 1, alpha, beta, new_board.player2)
                        if current_board.evaluation < best_evaluation:
                            best_evaluation = current_board.evaluation
                            best_board = new_board

                            if best_evaluation <= alpha:
                                self.print_log(board, depth, current_board.evaluation, alpha, beta)
                                return best_board

                            if best_evaluation < beta:
                                beta = best_evaluation

                            self.print_log(board, depth, current_board.evaluation, alpha, beta)
                        else:
                            self.print_log(board, depth, best_evaluation, alpha, beta)

            return best_board

if __name__ == '__main__':
    solution = Solution()
