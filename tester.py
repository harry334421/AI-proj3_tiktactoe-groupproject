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

if __name__ == '__main__':
  unittest.main()
