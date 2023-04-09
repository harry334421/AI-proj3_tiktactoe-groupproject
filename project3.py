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
# project3.py - Main menu for creating and playing games


from project_httpclient import ProjectHttpClient
import TTTStrategy as strategy

import argparse
import numpy as np
import random
import time


LIST_GAMES = '1'
LIST_TEAMS = '1a'
CREATE_NEW_GAME = '2'
PLAY_SINGLE_MOVE = '3'
PLAY_WHOLE_EXISTING_GAME = '3a'
SHOW_GAME_MOVES = '4'
SHOW_GAME_MAP = '5'
SHOW_GAME_BOARD = '6'
EXIT_PROJECT3 = '7'

main_menu = {}
main_menu[LIST_GAMES] ="List games"
main_menu[LIST_TEAMS] = "List teams"
main_menu[CREATE_NEW_GAME] ="Create new game"
main_menu[PLAY_SINGLE_MOVE] ="Play single move"
main_menu[PLAY_WHOLE_EXISTING_GAME]="Play whole (existing) game"
main_menu[SHOW_GAME_MOVES]="Show moves for existing game"
main_menu[SHOW_GAME_MAP]="Show map for existing game"
main_menu[SHOW_GAME_BOARD]="Show board for existing game"
main_menu[EXIT_PROJECT3]="Exit"

my_games = []
my_game_ids = []


def read_token_file():
    my_id = 0
    my_key = ""
    with open('token.txt') as f:
        for line in f:
            if not line.startswith("#"):
                values = line.split(',')
                my_id = values[0]
                my_key = values[1].strip()
                break
    return my_id,  my_key


def print_main_menu():
    print("Main menu")
    print("---------")
    for entry in main_menu.keys():
        print(f"{entry}. {main_menu[entry]}")


def update_internal_gamelist():
    # Updating  copies
    global my_games
    global my_game_ids

    my_games_raw = phc.get_my_games()
    my_games = {}
    my_game_ids = []
    for gamemap in my_games_raw:
        # Single ID in each map
        game_id = int(list(gamemap.keys())[0])
        game_str = list(gamemap.values())[0]
        my_game_ids.append(game_id)
        my_games[game_id] = game_str


def list_games():
    print(f"Listing games for {my_id}...\n")
    update_internal_gamelist()
    print(f"Games for {my_id}: {my_games}")


def list_teams():
    print(f"Teams for {my_id}: {phc.teams}")


def create_new_game():
    print("Creating new game...")
    team1_id = input("Team 1 ID: ")
    team2_id = input("Team 2 ID: ")
    board_size = input("Board size: ")
    target_size = input("Target size (consecutive symbols for win): ")
    phc.create_new_game(board_size,  target_size, team1_id,  team2_id)


def play_single_move():
    game_id = input("Game ID: ")
    games_list = phc.get_my_games()
    game_exists = False
    game_str = ""
    for game_desc_map in games_list:
        if game_id in game_desc_map.keys():
            game_str = game_desc_map[game_id]
            game_exists = True
            break

    if not game_exists:
        print(f"Error: {game_id} is not in the list of current games: {games_list}")
        # Go back into the main menu
        return

    # game_str is in format '<player1>:<player2>:<symbol of current player>'
    game_setup = game_str.split(':')
    team1_id = int(game_setup[0])
    team2_id = int(game_setup[1])

    # Good chance that no moves exist yet - shouldn't be an error
    last_move_raw = phc.get_moves(game_id, 1,  quiet=True)
    current_team_id = team1_id
    # If there are no moves yet, it is the first player's turn by default
    if last_move_raw:
        last_move = last_move_raw[0]
        # Switch players if Player 1 just went
        if int(last_move['teamId']) == current_team_id:
            current_team_id = team2_id

    # Is it allowable to play? Am I a part of the team playing?
    if not current_team_id in phc.teams:
        print(f"Error: {my_id} is not a member of the current turn's team ({current_team_id})")
        # Go back to the main menu
        return

    row = input("Row (y-coordinate): ")
    col = input("Column (x-coordinate): ")
    print(f"Playing single move for {current_team_id} (with upper-left as origin)...\n")

    phc.make_move(game_id,  current_team_id, row,  col)


# Is it the turn of a team I am part of?
def is_my_turn(game_id,  server_player1,  server_player2):
    my_turn = False
    my_moves = phc.get_moves(game_id,  1)
    current_team_id = -1
    last_move = []

    if not my_moves:
        print(f"It is Player 1 ({server_player1})'s turn)")
        current_team_id = server_player1
    else:
        last_move = my_moves[0]
        last_team_id = int(last_move['teamId'])
        if (last_team_id == server_player1):
            print(f"It is Player 2 ({server_player2})'s turn")
            current_team_id = server_player2
        else:
            print(f"It is Player 1 ({server_player1})'s turn")
            current_team_id = server_player1

    # Am I allowed to play?
    if current_team_id in phc.teams:
        print(f"I can make a move because {current_team_id} includes me")
        my_turn = True
    else:
        print(f"I need to wait until {current_team_id} makes a move")
        my_turn = False

    return my_turn,  current_team_id,  last_move


#String to NP Array
def string_to_board(boardstr):
    ele_dict={"X":-1, "O":1, "_":0, "-":0}
    rows=boardstr.split("\n")
    rows.remove("")
    if " " in rows[0]:
        board=np.array([[ele_dict[ele] for ele in row.split(" ")] for idx, row in enumerate(rows)])
    else:
        board=np.array([[ele_dict[ele] for ele in [*row]] for idx, row in enumerate(rows)])
    return board


# Are there any empty spots left on the board?
def is_full(board):
    return all(0 not in row for row in board)


def print_board(board):
    for row in board:
        print(" ".join(["X" if x == -1 else "O" if x == 1 else "_" for x in row]))
    print()


# Quickly find an usused space (for testing mostly)
def select_unused_coords(board):
    board_size = board.shape[0]
    row = 0
    col = 0
    while True:
        row = random.randrange(board_size)
        col = random.randrange(board_size)
        if board[row][col] == 0:
            break
    print(f"Selected row={row}, col={col} for board =")
    print_board(board)

    return row, col


def is_game_over(board, target, row, col):
    game_over = False
    winner_value = 0

    current_winner = strategy.check_winner(board, target, row,  col)
    if current_winner != 0:
        # Game has been won already
        game_over = True
        winner_value = current_winner

    elif current_winner == 0 and strategy.is_full(board):
        # Nobody won and nobody will
        game_over = True
        winner_value = 0

    return game_over,  winner_value


def print_winner(winner_value,  server_player1,  server_player2, game_id):
    if winner_value == 1:
        # Maximizing player won
        print(f"Player 1 ({server_player1}) won game {game_id}")
    elif winner_value == -1:
        # Minimizing player won
        print(f"Player 2 ({server_player2}) won game {game_id}")
    elif winner_value == 0:
        print(f"Draw for game {game_id}")


def play_existing_game():
    print("Getting the move list...\n")

    game_id = int(input("Game ID: "))
    if not game_id in my_game_ids:
        update_internal_gamelist()

    if not game_id in my_game_ids:
        print(f"Error: {game_id} is not in the list of existing games {my_game_ids}")
        return

    target = int(input("Target size: "))

    # Figure out player identities
    server_players_raw = my_games[game_id].split(':')
    server_player1 = int(server_players_raw[0]) # Maximizing player
    server_player2 = int(server_players_raw[1]) # Minimizing player
    print(f"Server: For game {game_id}, player1={server_player1}, player2={server_player2}")

    existing_moves = phc.get_moves(game_id,  1)
    # If a move exists, it is possible that the game is over already
    if existing_moves:
        last_move = existing_moves[0]
        last_x = int(last_move['moveX'])
        last_y = int(last_move['moveY'])
        last_row = last_y
        last_col = last_x
        print(f"Checking last move of row={last_row},col={last_col}")
        boardstr = phc.get_game_board(game_id)
        board = string_to_board(boardstr)
        current_winner = strategy.check_winner(board, target, last_row,  last_col)
        if current_winner != 0:
            print_winner(current_winner, server_player1,  server_player2,  game_id)
            return

    while True:
        my_turn,  current_team_id,  prev_move = is_my_turn(game_id,  server_player1,  server_player2)
        if not my_turn:
            delay = 10
            print(f"Waiting for {delay} seconds")
            time.sleep(delay)
        else:
            boardstr = phc.get_game_board(game_id)
            board = string_to_board(boardstr)
            # TODO - Get the actual target
            target = board.shape[0]

            # If there are existing moves, make sure the game is still going
            if prev_move:
                row = int(prev_move['moveY'])
                col = int(prev_move['moveX'])
                current_winner = strategy.check_winner(board, target, row,  col)
                if current_winner != 0:
                    # Game has been won already
                    print_winner(current_winner,  server_player1,  server_player2,  game_id)
                    break
                elif current_winner == 0 and strategy.is_full(board):
                    # Nobody won and nobody will
                    print_winner(current_winner,  server_player1,  server_player2,  game_id)
                    break

            # Since the game hasn't finished, make a move
            # TODO - Use the TTTStrategy, TTTMover...
            row, col = select_unused_coords(board)
            phc.make_move(game_id,  current_team_id, row,  col)

            # Did this last move win the game?
            current_winner = strategy.check_winner(board, target, row,  col)
            if current_winner != 0:
                # Game has been won already
                print_winner(current_winner,  server_player1,  server_player2,  game_id)
                break
            elif current_winner == 0 and strategy.is_full(board):
                # Nobody won and nobody will
                print_winner(current_winner,  server_player1,  server_player2,  game_id)
                break
        time.sleep(5)


def show_game_moves():
    print("Getting the move list...\n")
    game_id = input("Game ID: ")
    count = input("Count (number of moves in the past to get): ")
    my_moves = phc.get_moves(game_id,  count)
    print(my_moves)


def show_game_map():
    print("Getting the game map...\n")
    game_id = input("Game ID: ")
    my_map = phc.get_game_map(game_id)
    if my_map:
        print(my_map)
    else:
        print(f"No moves yet for {game_id}")


def show_game_board():
    print("Getting the game board...\n")
    game_id = input("Game ID: ")
    my_board = phc.get_game_board(game_id)
    print(my_board)


# Using the project HTTP client is possible here if the project is run as a script
# python3 ./project3.py
if __name__=='__main__':
    # Adding the '-d' command line argument to play against the dummy server
    parser = argparse.ArgumentParser(prog='project3',
                                                                description='Generalized TicTacToe game')
    parser.add_argument('-d','--dummy',
                                        action='store_true',
                                        help="Play against the dummy server instead of the real one" )
    args = parser.parse_args()

    # ID and token are used for server authentication
    my_id,  my_key = read_token_file()
    phc = ProjectHttpClient(my_id,  my_key,  args.dummy)

    while True:
        print_main_menu()
        selection = input("\nSelection: ").strip()

        if selection == LIST_GAMES:
            list_games()
        elif selection == LIST_TEAMS:
            list_teams()
        elif selection == CREATE_NEW_GAME:
            create_new_game()
        elif selection == PLAY_SINGLE_MOVE:
            play_single_move()
        elif selection == PLAY_WHOLE_EXISTING_GAME:
            play_existing_game()
        elif selection == SHOW_GAME_MOVES:
            show_game_moves()
        elif selection == SHOW_GAME_MAP:
            show_game_map()
        elif selection == SHOW_GAME_BOARD:
            show_game_board()
        elif selection == EXIT_PROJECT3:
            print("Exiting...")
            break
        else:
            print(f"{selection} is invalid")

        print("\n")
