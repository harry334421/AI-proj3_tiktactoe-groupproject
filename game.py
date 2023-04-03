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
# game.py - Handle some of the game mechanics for playing Tic-Tac-Toe


from tictactoe import TicTacToe


class Game:
    # Constructor
    def __init__(self,  team1,  team2, board_size=3,  target_size=3,  game_id=1):
        self.player1 = team1
        self.player2 = team2
        self.board_size = board_size
        self.target_size = target_size
        self.game_id = game_id
        self.is_player1_turn = True
        self.ttt = TicTacToe(board_size, target_size)
        self.moves_made = []
        self.game_over = False
        # For (roughly) simulating a server - not useful for the client by itself
        self.move_id_counter = 1000


    def make_move(self,  team,  row,  col):
        team_is_player1 = team == self.player1
        if self.ttt.is_valid_move(team_is_player1,  row, col):
            self.ttt.make_move(team_is_player1, row, col)
            # Store the move for records
            current_move = {}
            current_move['moveId'] = self.move_id_counter
            current_move['gameId'] = self.game_id
            current_move['teamId'] = team
            current_move['symbol'] = self.team_symbol(team)
            # Assuming columns are x coordinate and rows are y coordinate
            current_move['move'] = f"{col},{row}"
            current_move['moveX'] = col
            current_move['moveY'] = row

            self.moves_made.append(current_move)
            self.move_id_counter += 1
        else:
            print("Error occurred: move now canceled")


    def whose_turn(self):
        if self.ttt.is_player1_turn():
            return self.player1
        else:
            return self.player2


    def team_symbol(self,  team):
        default_symbol = '-'
        if team == self.player1:
            return 'X'
        elif team == self.player2:
            return 'O'
        else:
            return default_symbol


    def get_moves(self):
        return self.moves_made


    def is_valid_move(self,  team,  row,  col):
        is_player1 = (team == self.whose_turn())
        return self.ttt.is_valid_move(is_player1, row, col)


    def is_game_over(self):
        return self.ttt.game_over


    def get_board(self):
        return self.ttt.get_board()


    def get_map(self):
        return self.ttt.get_map()


    def get_winner(self):
        winner_id = -1 # Invalid winner ID to start
        if self.ttt.winner == 1:
            winner_id = self.player1
        elif self.ttt.winner == -1:
            winner_id = self.player2

        return winner_id


    def __str__(self):
        ret = (f"player1_id={self.player1}, player2_id={self.player2}, "
                    f"game_id={self.game_id}, Whose turn? id={self.whose_turn()}\n"
                    f"{self.ttt}")
        return ret


if __name__=='__main__':
    game = Game(team1=1, team2=3)
    print(game)
    print(f"It is {game.whose_turn()}'s turn")
    game.make_move(team=1, row=1, col=1)
    print(f"After a move was made,  it is now {game.whose_turn()}'s turn")
    print(game)
    print(f"The game map is now {game.get_map()}")
