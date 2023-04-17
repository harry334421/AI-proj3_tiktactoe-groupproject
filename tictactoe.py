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

import TTTStrategy as strategy

import numpy as np
import random


class TicTacToe:
    # Constructor
    def __init__(self,  board_size,  target_size):
        self.board_size = board_size
        self.target = target_size
        self.board = np.zeros([board_size, board_size])
        self.player1_turn = True
        self.moves = []
        self.game_over = False
        self.winner_value = 0 # Draw to start


    # Visual representation of the board
    def print_board(self):
        print(self.board_to_string(self.board))


    def board_to_string(self,  board):
        rows,  cols = self.board.shape
        boardstr = str()
        for row in range(rows):
            for col in range(cols):
                if self.board[row][col] == 1:
                    boardstr += "X"
                elif self.board[row][col] == -1:
                    boardstr += "O"
                else:
                    boardstr += "-"

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
        winner_value = strategy.check_winner(self.board, self.target, row,  col)
        if winner_value != 0:
            self.game_over = True
            self.winner_value = winner_value
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

            # Just use the random strategy
            row = 0
            col = 0
            while True:
                row = random.randrange(self.board_size)
                col = random.randrange(self.board_size)
                if self.board[row][col] == 0:
                    break
            self.make_move(self.is_player1_turn(), row, col)
            self.print_board()

            winner = strategy.check_winner(self.board, self.target, row,  col)
            if winner != 0 or self.is_full(self.board):
                break

        if winner == 1:
            print("Player 1 (Maximizing player) wins!")
        elif winner == -1:
            print("Player 2 (Minimizing player) wins!")
        else:
            print("It's a draw!")


    def get_map(self):
        rows,  cols = self.board.shape
        move_map = {}
        for row in range(rows):
            for col in range(cols):
                key = f"{col},{row}"
                # Player 1
                if self.board[row][col] == 1:
                    move_map[key] = 'X'
                # Player 2
                elif self.board[row][col] == -1:
                    move_map[key] = 'O'
                # Otherwise do nothing...

        return str(move_map)


    def get_board(self):
        return self.board_to_string(self.board)


    def __str__(self):
        # Just print the board
        return self.board_to_string(self.board)


if __name__=='__main__':
    # Set your desired board size and target, then start the game
    board_size = 8
    target_size = 5
    ttt = TicTacToe(board_size, target_size)
    ttt.play_self_contained_game()
