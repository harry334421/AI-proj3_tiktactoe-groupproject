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


from game import Game
from strategy_random import StrategyRandom

import ast
from bottle import request,  route,  run
import json
import urllib.parse


query_counter = 0
game_id_counter = 2000
move_id_counter = 0
all_games = {}
server_id = 9999
strategy = StrategyRandom()

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
    elif query_type == 'moves':
        resp = handle_request_moves(query)
    elif query_type == 'boardString':
        resp = handle_request_board_string(query)
    elif query_type == 'boardMap':
        resp = handle_request_board_map(query)
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
            team1 = int(query['teamId1'][0])
            team2 = int(query['teamId2'][0])
            game_id = game_id_counter

            new_game = Game(team1, team2, board_size, target, game_id)
            all_games[game_id_counter] = new_game

            # Make the initial move if it is the server's turn
            if server_id == int(new_game.player1):
                row, col = strategy.select_next_move_coords(new_game.ttt, server_id==new_game.player1)
                new_game.make_move(server_id, row, col)

            resp = {}
            resp['code'] = "OK"
            resp['gameId'] = game_id_counter
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
    my_games = {}
    for game in all_games.values():
        game_str = f"{game.player1}:{game.player2}:{game.team_symbol(game.whose_turn())}"
        my_games[game.game_id] = game_str
    resp["myGames"] = my_games

    return resp


def handle_move(query):
    global move_id_counter
    query_type = query['type'][0]

    # Assuming failure by default
    # - Does the game exist?
    # - Is the team a participant in the game
    # - Is it the turn of the player making the move?
    # - Are the move dimensions valid?
    # - Has the game already been won?
    resp = {}
    resp['code'] = "FAIL"

    if not 'gameId' in query or \
        not 'teamId' in query or \
        not 'move' in query:
            resp["message"] = f"Invalid '{query_type}' command: query={query}"
            return resp

    game_id = int(query['gameId'][0])
    team_id = int(query['teamId'][0])

    move_list = ast.literal_eval(query['move'][0])
    row = move_list[1]
    col = move_list[0]
    if not game_id in all_games.keys():
        resp["message"] = f"Game '{game_id}' does not exist: query={query}"
        return resp

    current_game = all_games[game_id]
    if not team_id == int(current_game.player1) and not team_id == int(current_game.player2):
        resp["message"] = f"Team {team_id} is not involved in game {game_id}: query={query}"
        return resp

    if not team_id == current_game.whose_turn():
        resp["message"] = f"It is not {team_id}'s turn: query={query}"
        return resp

    if not current_game.is_valid_move(team_id, row, col):
        resp["message"] = f"Invalid move: query={query}"
        return resp

    if current_game.is_game_over():
        resp["message"] = f"Game already over: winner={current_game.winner()},  query={query}"
        return resp

    # Passed all the tests, can finally make the move
    current_game.make_move(team_id, row, col)

    resp['code'] = "OK"
    resp['moveId'] = move_id_counter
    move_id_counter += 1

    if not current_game.is_game_over():
        # TODO - Place this elsewhere so a delay can be introduced
        if team_id == int(current_game.player1):
            server_id = int(current_game.player2)
        else:
            server_id = int(current_game.player1)
        row, col = strategy.select_next_move_coords(current_game.ttt,  server_id==current_game.player1)
        current_game.make_move(server_id, row, col)

    return resp


def handle_request_board_string(query):
    query_type = query['type'][0]

    # Assuming failure by default
    resp = {}
    resp['code'] = "FAIL"

    if not 'gameId' in query:
        resp["message"] = f"Invalid '{query_type}' command: query={query}"
    elif not int(query['gameId'][0]) in all_games.keys():
        resp["message"] = f"Game ID invalid: query={query}"
    else:
        game_id = int(query['gameId'][0])
        current_game = all_games[game_id]
        resp['code'] = "OK"
        resp['output'] = current_game.get_board()

    return resp


def handle_request_board_map(query):
    query_type = query['type'][0]

    # Assuming failure by default
    resp = {}
    resp['code'] = "FAIL"

    if not 'gameId' in query:
        resp["message"] = f"Invalid '{query_type}' command: query={query}"
    elif not int(query['gameId'][0]) in all_games.keys():
        resp["message"] = f"Game ID invalid: query={query}"
    else:
        game_id = int(query['gameId'][0])
        current_game = all_games[game_id]
        resp['code'] = "OK"
        resp['output'] = current_game.get_map()

    return resp


def handle_request_moves(query):
    query_type = query['type'][0]

    # Assuming failure by default
    resp = {}
    resp['code'] = "FAIL"

    if not 'gameId' in query:
        resp["message"] = f"Invalid '{query_type}' command: query={query}"
        return resp

    if not int(query['gameId'][0]) in all_games.keys():
        resp["message"] = f"Game ID invalid: query={query}"
        return resp

    game_id = int(query['gameId'][0])
    count = int(query['count'][0])
    current_game = all_games[game_id]
    all_moves = current_game.get_moves()
    # Get just the last n moves
    wanted_moves = all_moves[-count:]

    resp['code'] = "OK"
    resp['moves'] = wanted_moves

    return resp


if __name__ == "__main__":
    run(host='localhost', port=8080, debug=True)
