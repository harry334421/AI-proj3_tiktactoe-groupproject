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


if __name__=='__main__':
    # Make sure API key and user ID are in memory
    with open('token.txt') as f:
        for line in f:
            if not line.startswith("#"):
                values = line.split(',')
                my_id = values[0]
                my_key = values[1].strip()
                break

    playing_real_server = False
    phc = ProjectHttpClient(my_id,  my_key,  playing_real_server)

    main_menu = {}
    main_menu['1']="List games"
    main_menu['2']="Create new game"
    main_menu['3']="Play single move"
    main_menu['4']="Show moves for existing game"
    main_menu['5']="Show map for existing game"
    main_menu['6']="Show board for existing game"
    main_menu['7']="Exit"

    while True:
        options = main_menu.keys()

        print("Main menu")
        print("---------")
        for entry in options:
            print(f"{entry}. {main_menu[entry]}")

        selection = input("\nSelection: ").strip()
        if selection =='1':
            print(f"Listing games for {my_id}...\n")
            phc.get_my_games()

        elif selection == '2':
            print(f"Creating new game for {my_id}...")
            team1_id = input("Team 1 ID: ")
            team2_id = input("Team 2 ID: ")
            board_size = input("Board size: ")
            target_size = input("Target size (consecutive symbols for win): ")
            me_first = (team1_id == my_id)
            if me_first:
                opponent_id = team2_id
            else:
                opponent_id = team1_id
            phc.create_new_game(board_size,  target_size, opponent_id,  me_first)

        elif selection == '3':
            print(f"Playing single move for {my_id} (with upper-left as origin)...\n")
            game_id = input("Game ID: ")
            row = input("Row (y-coordinate): ")
            col = input("Column (x-coordinate): ")
            phc.make_move(game_id,  row,  col)

        elif selection == '4':
            print("Getting the move list...\n")
            game_id = input("Game ID: ")
            count = input("Count (number of moves in the past to get): ")
            my_moves = phc.get_moves(game_id,  count)
            print(my_moves)

        elif selection == '5':
            print("Getting the game map...\n")
            game_id = input("Game ID: ")
            my_map = phc.get_game_map(game_id)
            print(my_map)

        elif selection == '6':
            print("Getting the game board...\n")
            game_id = input("Game ID: ")
            my_board = phc.get_game_board(game_id)
            print(my_board)

        elif selection == '7':
            print("Exiting...")
            break

        else:
            print(f"{selection} is invalid")

        print("\n")

# Create a few new games
#board_size = 3
#target_size = 3
#me_first = True
#phc.create_new_game(board_size,  target_size,  9999,  me_first)
#
#game_id = phc.get_my_games()[0]

# Now make moves using phc.make_move(game_id,row,col)
# ...
