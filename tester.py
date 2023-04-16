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
# tester.py - Unit test the components making up the game


from game import Game
import TTTStrategy as strategy

import numpy as np
import unittest


class Tester( unittest.TestCase ):

    def test_setup(self):
        my_id = 7777
        other_id = 8888
        game1 = Game(team1=my_id,  team2=other_id)
        self.assertEqual(game1.whose_turn(), my_id)
        game1.make_move(my_id, 0, 0)
        self.assertEqual(game1.whose_turn(), other_id)

        game2 = Game(team1=other_id,  team2=my_id)
        self.assertEqual(game2.whose_turn(), other_id)
        game2.make_move(other_id, 0, 0)
        self.assertEqual(game2.whose_turn(), my_id)

    def test_check_winner(self):
        board_size = 3
        target = 3
        board=np.array([[0]*board_size for i in range(board_size)])

        # Player 2 (minimizing) should win from lower left to upper right
        board[0] = [1,  1,  -1]
        board[1] = [1,  -1,  1]
        board[2] = [-1,  0,  0]

        self.assertEqual(-1, strategy.check_winner(board, target, 2, 0))
        self.assertEqual(-1, strategy.check_winner(board, target, 1, 1))
        self.assertEqual(-1, strategy.check_winner(board, target, 0, 2))

        # Player 2 (minimizing) should win from upper left to lower right
        board[0] = [-1,  1,  0]
        board[1] = [1,  -1, 1]
        board[2] = [1,  0, -1]

        self.assertEqual(-1, strategy.check_winner(board, target, 0, 0))
        self.assertEqual(-1, strategy.check_winner(board, target, 1, 1))
        self.assertEqual(-1, strategy.check_winner(board, target, 2, 2))

        # Player 1 (maximizing) should win from the center column
        board[0] = [-1,  1,  -1]
        board[1] = [0,  1,  0]
        board[2] = [0,  1,  0]

        self.assertEqual(1, strategy.check_winner(board, target, 0, 1))
        self.assertEqual(1, strategy.check_winner(board, target, 1, 1))
        self.assertEqual(1, strategy.check_winner(board, target, 2, 1))

        # Player 2 (minimizing) should win from the top row
        board[0] = [-1,  -1,  -1]
        board[1] = [0,  1,  0]
        board[2] = [0,  1,  1]

        self.assertEqual(-1, strategy.check_winner(board, target, 0, 0))
        self.assertEqual(-1, strategy.check_winner(board, target, 0, 1))
        self.assertEqual(-1, strategy.check_winner(board, target, 0, 2))

        # Player 1 (maximizing) should win from the middle row
        board[0] = [0,  -1,  0]
        board[1] = [1,  1,  1]
        board[2] = [0,  -1,  0]

        self.assertEqual(1, strategy.check_winner(board, target, 1, 0))
        self.assertEqual(1, strategy.check_winner(board, target, 1, 1))
        self.assertEqual(1, strategy.check_winner(board, target, 1, 2))

        # Class server game #4103
        # Issue - It seems like a win existed before the final move, hence the
        # test fails
        #XOX--
        #OXOXO
        #OXOXO
        #XOXOO
        #XOXOX
        # Final move at (2,2)
#        board_size = 5
#        target = 3
#        board=np.array([[0]*board_size for i in range(board_size)])
#        board[0] = [1,  -1,  1,  0,  0]
#        board[1] = [-1,  1,  -1,  1,  -1]
#        board[2] = [-1,  1,  -1,  1,  -1]
#        board[3] = [1,  -1,  1,  -1,  -1]
#        board[4] = [1,  -1,  1,  -1,  1]
#        self.assertEqual(-1,  strategy.check_winner(board, target, 2,  2))



if __name__ == '__main__':
  unittest.main()
