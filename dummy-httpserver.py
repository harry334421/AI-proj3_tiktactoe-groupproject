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
import urllib.parse

mycount = 0

@route('<mypath:path>', method=['GET', 'POST'])
def query_handler(mypath):
    global mycount

    mycount = mycount + 1
    print(f"count={mycount}")

    query = urllib.parse.parse_qs(request.query_string)
    resp = {}
    resp["code"] = "OK"

    query_type = query['type'][0]
    if query_type == 'game':
        # Check mandatory parameters
        if 'teamId1' in query and \
            'teamId2' in query and \
            query['gameType'][0] == 'TTT':
                # Check for optional parameters
                board_size = 20 # Default
                if 'boardSize' in query:
                    board_size = query['boardSize']
                target = 6 # Default
                if 'target' in query:
                    target = query['target']
                print(f"Valid {query_type} command: boardSize={board_size}, target={target}")

    elif query_type == 'myGames' or query_type == 'myOpenGames':
        # No other parameters...
        print(f"Valid {query_type} command")
    elif query_type == 'move':
        if 'gameId' in query and \
            'teamId' in query and \
            'move' in query:
                # TODO - Make the checks for valid items
                print(f"Valid {query_type} command")
    elif query_type == 'moves':
        if 'gameId' in query and \
            'count' in query:
            print(f"Valid {query_type} command")
    elif query_type == 'boardString':
        if 'gameId' in query:
            print(f"Valid {query_type} command")
    elif query_type == 'boardMap':
        if 'gameId' in query:
            print(f"Valid {query_type} command")
    else:
        err_msg = f"This server does not handle the '{query_type}' command"
        resp["code"] = "FAIL"
        resp["message"] = err_msg

    return json.dumps(resp)


if __name__ == "__main__":
    run(host='localhost', port=8080, debug=True)
