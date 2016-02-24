#!/usr/bin/python
import sys
import copy


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
