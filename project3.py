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

import argparse


LIST_GAMES = '1'
LIST_TEAMS = '1a'
CREATE_NEW_GAME = '2'
PLAY_SINGLE_MOVE = '3'
SHOW_GAME_MOVES = '4'
SHOW_GAME_MAP = '5'
SHOW_GAME_BOARD = '6'
EXIT_PROJECT3 = '7'

if __name__=='__main__':
    # Adding the '-d' command line argument to play against the dummy server
    parser = argparse.ArgumentParser(prog='project3',
                                                                description='Generalized TicTacToe game')
    parser.add_argument('-d','--dummy',
                                        action='store_true',
                                        help="Play against the dummy server instead of the real one" )
    args = parser.parse_args()

    # Make sure API key and user ID are in memory
    with open('token.txt') as f:
        for line in f:
            if not line.startswith("#"):
                values = line.split(',')
                my_id = values[0]
                my_key = values[1].strip()
                break

    phc = ProjectHttpClient(my_id,  my_key,  args.dummy)


    main_menu = {}
    main_menu[LIST_GAMES] ="List games"
    main_menu[LIST_TEAMS] = "List teams"
    main_menu[CREATE_NEW_GAME] ="Create new game"
    main_menu[PLAY_SINGLE_MOVE] ="Play single move"
    main_menu[SHOW_GAME_MOVES]="Show moves for existing game"
    main_menu[SHOW_GAME_MAP]="Show map for existing game"
    main_menu[SHOW_GAME_BOARD]="Show board for existing game"
    main_menu[EXIT_PROJECT3]="Exit"

    while True:
        options = main_menu.keys()

        print("Main menu")
        print("---------")
        for entry in options:
            print(f"{entry}. {main_menu[entry]}")

        selection = input("\nSelection: ").strip()

        if selection == LIST_GAMES:
            print(f"Listing games for {my_id}...\n")
            my_games = phc.get_my_games()
            print(f"Games for {my_id}: {my_games}")

        elif selection == LIST_TEAMS:
            print(f"Teams for {my_id}: {phc.teams}")

        elif selection == CREATE_NEW_GAME:
            print("Creating new game...")
            team1_id = input("Team 1 ID: ")
            team2_id = input("Team 2 ID: ")
            board_size = input("Board size: ")
            target_size = input("Target size (consecutive symbols for win): ")
            phc.create_new_game(board_size,  target_size, team1_id,  team2_id)

        elif selection == PLAY_SINGLE_MOVE:
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
                continue

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
                continue

            row = input("Row (y-coordinate): ")
            col = input("Column (x-coordinate): ")
            print(f"Playing single move for {current_team_id} (with upper-left as origin)...\n")

            phc.make_move(game_id,  current_team_id, row,  col)

        elif selection == SHOW_GAME_MOVES:
            print("Getting the move list...\n")
            game_id = input("Game ID: ")
            count = input("Count (number of moves in the past to get): ")
            my_moves = phc.get_moves(game_id,  count)
            print(my_moves)

        elif selection == SHOW_GAME_MAP:
            print("Getting the game map...\n")
            game_id = input("Game ID: ")
            my_map = phc.get_game_map(game_id)
            if my_map:
                print(my_map)
            else:
                print(f"No moves yet for {game_id}")

        elif selection == SHOW_GAME_BOARD:
            print("Getting the game board...\n")
            game_id = input("Game ID: ")
            my_board = phc.get_game_board(game_id)
            print(my_board)

        elif selection == EXIT_PROJECT3:
            print("Exiting...")
            break

        else:
            print(f"{selection} is invalid")

        print("\n")
