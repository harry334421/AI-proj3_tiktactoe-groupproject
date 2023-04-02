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
# tictactoe.py - Generalized Tic-Tac-Toe game (board and operations)


#import math
#import copy
import random
#import time
import numpy as np
#from multiprocessing import Manager, Pool, cpu_count

# Adjustable thresholds when using multiprocessing
#TIMEOUT=5
#cpu=cpu_count()-1


class TicTacToe:
    # Constructor
    def __init__(self,  board_size,  target_size):
        self.board_size = board_size
        self.target = target_size
        self.board = np.zeros([board_size, board_size])
        self.player1_turn = True
        self.moves = []


    # Visual representation of the board
    def print_board(self):
        print(self.board_to_string(self.board))


    def board_to_string(self,  board):
        boardstr = str()
        for row in board:
            boardstr += " ".join(["X" if x == 1 else "O" if x == -1 else "_" for x in row])
            boardstr += "\n"
        return boardstr


    def string_to_board(self, boardstr):
        ele_dict={"O":-1, "X":1, "_":0, "-":0}
        rows=boardstr.split("\n")
        rows.remove("")
        if " " in rows[0]:
            board=[[ele_dict[ele] for ele in row.split(" ")] for idx, row in enumerate(rows)]
        else:
            board=[[ele_dict[ele] for ele in [*row]] for idx, row in enumerate(rows)]
        return board


    # Does the board have a winner?
    def check_winner(self,  board,  target):
        rows = len(board)
        cols = len(board[0])
        # Check rows
        for row in range(rows):
            for col in range(cols - target + 1):
                window = board[row][col:col + target]
                if all(val == 1 for val in window):
                    return 1
                elif all(val == -1 for val in window):
                    return -1
        # Check columns
        for row in range(rows - target + 1):
            for col in range(cols):
                window = [board[row + i][col] for i in range(target)]
                if all(val == 1 for val in window):
                    return 1
                elif all(val == -1 for val in window):
                    return -1
        # Check diagonals (top-left to bottom-right)
        for row in range(rows - target + 1):
            for col in range(cols - target + 1):
                window = [board[row + i][col + i] for i in range(target)]
                if all(val == 1 for val in window):
                    return 1
                elif all(val == -1 for val in window):
                    return -1
        # Check diagonals (top-right to bottom-left)
        for row in range(rows - target + 1):
            for col in range(target - 1, cols):
                window = [board[row + i][col - i] for i in range(target)]
                if all(val == 1 for val in window):
                    return 1
                elif all(val == -1 for val in window):
                    return -1
        return 0


    # Have all the possible moves been made?
    def is_full(self, board):
        for row in board:
            if 0 in row:
                return False
        return True


    #Check Immediate Winning Move
    def is_winning_move(self, board,  target,  row, col):
        is_player1 = board[row][col]
        #Check Winner
        if self.check_winner(board, target)==is_player1:
            return True
        return False


    # Making a move (assuming that it is allowed for the given player)
    # For Player 1, the result is maximized.
    # For Player 2, the result is minimized
    def make_move(self, is_player1, row, col):
        if is_player1 != self.player1_turn:
            print("Error! Not the selected player's turn")
            return

        piece_value = 1
        if not is_player1:
            piece_value = -1

        self.board[row][col] = piece_value
        self.player1_turn = not self.player1_turn
        return row, col


    def select_next_move_coords(self,  is_player1):
        row = 0
        col = 0
        # TODO - add the sophisticated logic using is_player1
        while True:
            row = random.randrange(self.board_size)
            col = random.randrange(self.board_size)
            if self.board[row][col] == 0:
                break

        return row, col


    def is_player1_turn(self):
        return self.player1_turn


    def is_valid_move(self,  is_player1,  row,  col):
        # A move is valid if
        # - coordinates fit on the board
        # - move is made by the correct player
        # - no token exists on the selected space
        valid_move = False
        if row < 0 or row >= self.board_size or col < 0 or col >= self.board_size:
            print(f"Error: Invalid move ({col},{row}): coordinates out of range")
        elif is_player1 != self.is_player1_turn():
            print(f"Error: Invalid move ({col},{row}): incorrect player's turn")
        elif self.board[row][col] != 0:
             print(f"Error: Invalid move ({col},{row}): Space not empty")
        else:
            valid_move = True

        return valid_move


    def play_self_contained_game(self):
        while True:
            if self.is_player1_turn():
                # Player 1 (Maximizing player)
                print(f'Player {"X"}')
            else:
                # Player 2 (Minimizing player)
                print(f'Player {"O"}')

            row, col = self.select_next_move_coords(self.is_player1_turn())
            self.make_move(self.is_player1_turn(), row, col)
            self.print_board()

            winner = self.check_winner(self.board, self.target)
            if winner != 0 or self.is_full(self.board):
                break

        if winner == 1:
            print("Player 1 (Maximizing player) wins!")
        elif winner == -1:
            print("Player 2 (Minimizing player) wins!")
        else:
            print("It's a draw!")


    def __str__(self):
        # Just print the board
        return self.board_to_string(self.board)


if __name__=='__main__':
    # Set your desired board size and target, then start the game
    board_size = 8
    target_size = 5
    ttt = TicTacToe(board_size, target_size)
    ttt.play_self_contained_game()
