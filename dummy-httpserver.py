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
#        # No other parameters...
#        print(f"Valid {query_type} command")
#    elif query_type == 'move':
#        if 'gameId' in query and \
#            'teamId' in query and \
#            'move' in query:
#                # TODO - Make the checks for valid items
#                print(f"Valid {query_type} command")
#    elif query_type == 'moves':
#        if 'gameId' in query and \
#            'count' in query:
#            print(f"Valid {query_type} command")
#    elif query_type == 'boardString':
#        if 'gameId' in query:
#            print(f"Valid {query_type} command")
#    elif query_type == 'boardMap':
#        if 'gameId' in query:
#            print(f"Valid {query_type} command")
    else:
        err_msg = f"This server does not handle the '{query_type}' command"
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
            resp['gameid'] = game_id_counter
            print(f"Valid {query_type} command: boardSize={board_size}, target={target}")
            new_ttt = TicTacToe(board_size, target)
            all_games[game_id_counter] = new_ttt
            game_id_counter += 1
    else:
        resp = {}
        resp["code"] = "FAIL"
        resp["message"] = f"This server does not handle the '{query_type}' command"
    return resp


def handle_get_my_games(query):
    # Much simpler than the real server's implementation - all games include the client
    resp = {}
    resp["code"] = "OK"
    resp["games"] = list(all_games.keys())

    return resp

if __name__ == "__main__":
    run(host='localhost', port=8080, debug=True)
