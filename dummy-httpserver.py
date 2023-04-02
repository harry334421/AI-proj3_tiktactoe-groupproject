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
# dummy_httpserver.py - HTTP server used for testing the client

from bottle import request,  route,  run
import json
from tictactoe import TicTacToe
import urllib.parse

query_counter = 0
game_id_counter = 2000
move_id_counter = 0
all_games = {}

# Note: the dummy server will handle a mismatch between the method and the
# command but the real server won't...
@route('<mypath:path>', method=['GET', 'POST'])
def query_handler(mypath):
    global query_counter

    query_counter = query_counter + 1
    print(f"Handling query {query_counter}")

    query = urllib.parse.parse_qs(request.query_string)
    query_type = query['type'][0]

    if query_type == 'game':
        resp = handle_create_game(query)
    elif query_type == 'myGames' or query_type == 'myOpenGames':
        resp = handle_get_my_games(query)
    elif query_type == 'move':
        resp = handle_move(query)
#    elif query_type == 'moves':
#        if 'gameId' in query and \
#            'count' in query:
#            print(f"Valid {query_type} command")
    elif query_type == 'boardString':
        resp = handle_request_board_string(query)
#    elif query_type == 'boardMap':
#        if 'gameId' in query:
#            print(f"Valid {query_type} command")
    else:
        err_msg = f"This server does not handle the '{query_type}' command"
        resp = {}
        resp["code"] = "FAIL"
        resp["message"] = err_msg

    return json.dumps(resp)


def handle_create_game(query):
    global game_id_counter
    query_type = query['type'][0]

    # Check mandatory parameters
    if 'teamId1' in query and \
        'teamId2' in query and \
        query['gameType'][0] == 'TTT':
            # Check for optional parameters
            board_size = 20 # Default
            if 'boardSize' in query:
                board_size = int(query['boardSize'][0])
            target = 6 # Default
            if 'target' in query:
                target = int(query['target'][0])

            resp = {}
            resp['code'] = "OK"
            resp['gameId'] = game_id_counter
            print(f"Valid {query_type} command: boardSize={board_size}, target={target}")
            new_ttt = TicTacToe(board_size, target)
            all_games[game_id_counter] = new_ttt
            game_id_counter += 1
    else:
        resp = {}
        resp["code"] = "FAIL"
        resp["message"] = f"Invalid '{query_type}' command: query={query}"
    return resp


def handle_get_my_games(query):
    # Much simpler than the real server's implementation - all games include the client
    resp = {}
    resp["code"] = "OK"
    resp["games"] = list(all_games.keys())

    return resp


def handle_move(query):
    global move_id_counter
    query_type = query['type'][0]

    # Assuming failure by default
    # TODO - Make an actual check of the board to see if valid move
    # - Is it the move for the proper player?
    # - Is the move within bounds?
    # - Is the move on top of a taken space?
    resp = {}
    resp['code'] = "FAIL"
    resp['message'] = f"Generic error for query={query}"

    if not 'gameId' in query or \
        not 'teamId' in query or \
        not 'move' in query:
            resp = {}
            resp["code"] = "FAIL"
            resp["message"] = f"Invalid '{query_type}' command: query={query}"
    else:
        gameId = int(query['gameId'][0])
        #lteamId = int(query['teamId'][0]) # TODO - Use teamId to check if it's for the right turn
        if not gameId in all_games.keys():
            resp["message"] = f"Game ID invalid: query={query}"
        # TODO - elif move for the given game is invalid...
        else:
            resp['code'] = "OK"
            resp['moveId'] = move_id_counter
            move_id_counter += 1

    return resp


def handle_request_board_string(query):
    query_type = query['type'][0]

    # Assuming failure by default
    resp = {}
    resp['code'] = "FAIL"
    resp['message'] = f"Generic error for query={query}"

    if not 'gameId' in query:
        resp["message"] = f"Invalid '{query_type}' command: query={query}"
    elif not int(query['gameId'][0]) in all_games.keys():
        resp["message"] = f"Game ID invalid: query={query}"
    else:
        game_id = int(query['gameId'][0])
        current_game = all_games[game_id]
        resp['code'] = "OK"
        resp['output'] = current_game.board_to_string( current_game.board )

    return resp


if __name__ == "__main__":
    run(host='localhost', port=8080, debug=True)
