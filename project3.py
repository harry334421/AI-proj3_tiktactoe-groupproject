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
import TTTMoveMaker as mm

import argparse
import json
import numpy as np
import os.path
import random
import time

import sys
import traceback # For debugging


LIST_GAMES = '1'
LIST_TEAMS = '2'
CREATE_NEW_GAME = '3'
PLAY_EXISTING_GAME = '4'
SHOW_GAME_MOVES = '5'
SHOW_GAME_MAP = '6'
SHOW_GAME_BOARD = '7'
EXIT_PROJECT3 = '8'

main_menu = {}
main_menu[LIST_GAMES] ="List games"
main_menu[LIST_TEAMS] = "List teams"
main_menu[CREATE_NEW_GAME] ="Create new game"
main_menu[PLAY_EXISTING_GAME]="Play existing game"
main_menu[SHOW_GAME_MOVES]="Show moves for existing game"
main_menu[SHOW_GAME_MAP]="Show map for existing game"
main_menu[SHOW_GAME_BOARD]="Show board for existing game"
main_menu[EXIT_PROJECT3]="Exit"

KEY_FILE = 'key.json'
SETTINGS_FILE = 'settings.json'

my_games = []
my_game_ids = []
my_settings = []


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
    print(f"Listing games for {phc.my_user_id}...\n")
    update_internal_gamelist()
    print(f"Games for User {phc.my_user_id} of teams {phc.teams}: {my_games}")


def list_teams():
    print(f"Teams for {phc.my_user_id}: {phc.teams}")


def create_new_game():
    print("Creating new game...")
    team1_id = input("Team 1 ID: ")
    team2_id = input("Team 2 ID: ")
    board_size = input("Board size: ")
    target_size = input("Target size (consecutive symbols for win): ")
    phc.create_new_game(board_size,  target_size, team1_id,  team2_id)


# Is it the turn of a team I am part of?
def is_my_turn(game_id,  server_player1,  server_player2):
    my_turn = False
    my_moves = phc.get_moves(game_id,  1)
    current_team_id = -1
    current_team_value = 0
    last_move = []

    if not my_moves:
        print(f"It is Player 1 ({server_player1})'s turn)")
        current_team_id = server_player1
        current_team_value = 1
    else:
        last_move = my_moves[0]
        last_team_id = int(last_move['teamId'])
        if (last_team_id == server_player1):
            print(f"\nIt is Player 2 ({server_player2})'s turn")
            current_team_id = server_player2
            current_team_value = -1
        else:
            print(f"\nIt is Player 1 ({server_player1})'s turn")
            current_team_id = server_player1
            current_team_value = 1

    # Am I allowed to play?
    move_allowed = False
    if type(phc.teams) is list and current_team_id in phc.teams:
        move_allowed = True
    elif type(phc.teams) is int and current_team_id == phc.teams:
        move_allowed = True

    if move_allowed:
        print(f"I can make a move because Team {current_team_id} includes me (User {phc.my_user_id})")
        my_turn = True
    else:
        print(f"I (User {phc.my_user_id}) need to wait until Team {current_team_id} makes a move")
        my_turn = False

    return my_turn, current_team_id, current_team_value,  last_move


#String to NP Array
def string_to_board(boardstr):
    ele_dict={"X":1, "O":-1, "_":0, "-":0}
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


# Select the appropriate evaluator mentioned in the settings
def choose_evaluator(team_id):
    if not str(team_id) in my_settings['eval_choice']:
        print(f"{team_id} is not listed in the evaluator settings: {my_settings['eval_choice']}")
        return 0
    else:
        return int(my_settings['eval_choice'][str(team_id)])


def play_existing_game():
    print("Getting the move list...\n")

    game_id = int(input("Game ID: "))
    if not game_id in my_game_ids:
        update_internal_gamelist()

    if not game_id in my_game_ids:
        print(f"Error: {game_id} is not in the list of existing games {my_game_ids}")
        return

    boardstr, target = phc.get_game_board(game_id)

    # Figure out player identities
    server_players_raw = my_games[game_id].split(':')
    server_player1 = int(server_players_raw[0]) # Maximizing player
    server_player2 = int(server_players_raw[1]) # Minimizing player
    print(f"Server: For game {game_id}, player1={server_player1}, player2={server_player2}\n")

    existing_moves = phc.get_moves(game_id,  1)
    # If a move exists, it is possible that the game is over already
    if existing_moves:
        last_move = existing_moves[0]
        last_x = int(last_move['moveX'])
        last_y = int(last_move['moveY'])
        last_row = last_y
        last_col = last_x
        board = string_to_board(boardstr)
        current_winner = strategy.check_winner(board, target, last_row,  last_col)
        if current_winner != 0:
            print_winner(current_winner, server_player1,  server_player2,  game_id)
            return

    while True:
        my_turn, current_team_id, current_team_value,  prev_move = is_my_turn(game_id,  server_player1,  server_player2)

        boardstr, _ = phc.get_game_board(game_id)
        board = string_to_board(boardstr)

        # If there are existing moves, make sure the game is still going
        if prev_move:
            prev_row = int(prev_move['moveX'])
            prev_col = int(prev_move['moveY'])
            current_winner = strategy.check_winner(board, target, prev_row,  prev_col)
            if current_winner != 0:
                # Game has been won already
                print_winner(current_winner,  server_player1,  server_player2,  game_id)
                break
            elif current_winner == 0 and strategy.is_full(board):
                # Nobody won and nobody will
                print_winner(current_winner,  server_player1,  server_player2,  game_id)
                break

        # Make sure it is our turn
        if not my_turn:
            delay = 10
            print(f"Waiting for {delay} seconds")
            time.sleep(delay)
            # Query the server once again by restarting the loop
            continue

        # Since the game hasn't finished, make a move
        timeout = 30
        is_maximizing = (current_team_id == server_player1)
        evaluator = choose_evaluator(current_team_id)
        last_moves = phc.get_moves(game_id,  2) # make_move requires last two moves
        min_depth=max(min(1, len(strategy.get_possible_moves(board))-1),0)
        try:
            coords, _ = mm.make_move(board, is_maximizing, target, last_moves, evaluator, timeout,  min_depth)
            row = coords[0]
            col = coords[1]
            #row, col = select_unused_coords(board)
            print(f"About to try row={row}, col={col}")
            phc.make_move(game_id,  current_team_id, row,  col)

        except Exception:
            print("Exception in user code:")
            print("-"*60)
            traceback.print_exc(file=sys.stdout)
            print("-"*60)

        # Give the server some time to react
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
    my_map, target = phc.get_game_map(game_id)
    if my_map:
        print(f"For Game {game_id} with target size = {target}:\n{my_map}")
    else:
        print(f"No moves yet for {game_id}")


def show_game_board():
    print("Getting the game board...\n")
    game_id = input("Game ID: ")
    my_board, target = phc.get_game_board(game_id)
    print(f"For Game {game_id} with target size = {target}:\n{my_board}")


# Using the project HTTP client is possible here if the project is run as a script
# python3 ./project3.py
if __name__=='__main__':
    # Adding the '-d' command line argument to play against the dummy server
    parser = argparse.ArgumentParser(prog='project3',
                                                                description='Generalized TicTacToe game')
    parser.add_argument('-d','--dummy',
                                        action='store_true',
                                        help="Play against the dummy server instead of the real one" )
    parser.add_argument('-f','--forceteam',
                                        nargs=1,
                                        help="Limit client to using a single team's identity" )
    args = parser.parse_args()

    # 'key.json' contains the necessary authentication headers
    if not os.path.exists(KEY_FILE):
        print(f"Error: No key/header file {KEY_FILE} (Did you copy and fill in the template?)")
        exit(0)
    elif not os.path.exists(SETTINGS_FILE):
        print(f"Error: No settings file {SETTINGS_FILE}")
        exit(0)

    my_settings = json.load(open(SETTINGS_FILE, 'r'))
    phc = ProjectHttpClient(KEY_FILE,  args.dummy,  args.forceteam)

    while True:
        print_main_menu()
        selection = input("\nSelection: ").strip()

        if selection == LIST_GAMES:
            list_games()
        elif selection == LIST_TEAMS:
            list_teams()
        elif selection == CREATE_NEW_GAME:
            create_new_game()
        elif selection == PLAY_EXISTING_GAME:
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
