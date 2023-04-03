# -*- coding: utf-8; mode: python; tab-width: 4; indent-tabs-mode: nil -*-

# CSCI 6511: AI
# Project 3: Generalized Tic-Tac-Toe
# teamLHL
# - Eric Luo
# - Patrick Husson
# - Hao Liu
#
# April 19, 2023
#
# strategy_random.py - Select the next move for a game randomly


import random


class StrategyRandom:
    # Constructor
    def __init__(self,  ttt):
        self.ttt = ttt

    def select_next_move_coords(self,  is_player1):
        row = 0
        col = 0
        while True:
            row = random.randrange(self.ttt.board_size)
            col = random.randrange(self.ttt.board_size)
            if self.ttt.board[row][col] == 0:
                break

        return row, col
