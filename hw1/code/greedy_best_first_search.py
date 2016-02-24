#!/usr/bin/python

import copy
from heapq import *

"""
1. init with a original board
2. get next boards and put them in priority_queue
3. choose best one from priority_queue
"""


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