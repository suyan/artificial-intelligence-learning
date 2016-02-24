#!/usr/bin/python
import sys
import copy


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
