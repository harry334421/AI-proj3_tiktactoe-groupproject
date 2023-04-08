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

from bottle import get, post,  request,  run
import json
import urllib.parse


query_counter = 0
game_id_counter = 2000
move_id_counter = 0
all_games = {}
server_id = 9999
strategy = StrategyRandom()

@get('<mypath:path>')
def get_query_handler(mypath):
    global query_counter

    query_counter = query_counter + 1
    print(f"Handling query {query_counter}")

    query = urllib.parse.parse_qs(request.query_string)
    query_type = query['type'][0]

    if query_type == 'myGames' or query_type == 'myOpenGames':
        resp = handle_get_my_games(query)
    elif query_type == 'myTeams':
        resp = handle_get_my_teams(query)
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


# Handle POST calls
@post('<mypath:path>')
def post_handler(mypath):
    global query_counter

    query_counter = query_counter + 1
    print(f"Handling query {query_counter}")

    query_type = request.forms['type']
    resp = {}
    resp["code"] = "FAIL"
    post_args = {}
    print(f"query_type={query_type}")

    if query_type == 'game':
        # Pull all the parameters out
        post_args['type'] = request.forms['type']
        post_args['teamId1'] = request.forms['teamId1']
        post_args['teamId2'] = request.forms['teamId2']
        post_args['gameType'] = request.forms['gameType']
        if 'boardSize' in request.forms:
            post_args['boardSize'] = request.forms['boardSize']
        if 'target' in request.forms:
            post_args['target'] = request.forms['target']

        resp = handle_create_game(post_args)

    elif query_type == 'move':
        # Pull all the parameters out
        post_args['type'] = request.forms['type']
        post_args['gameId'] = request.forms['gameId']
        post_args['teamId'] = request.forms['teamId']
        post_args['move'] = request.forms['move']

        resp = handle_move(post_args)

    else:
        resp = {}
        resp["code"] = "FAIL"
        resp["message"] = f"This server does not handle the '{query_type}' command"

    return json.dumps(resp)


def handle_create_game(query):
    global game_id_counter
    query_type = query['type']

    # Check mandatory parameters
    if 'teamId1' in query and \
        'teamId2' in query and \
        query['gameType'] == 'TTT':
            # Check for optional parameters
            board_size = 20 # Default
            if 'boardSize' in query:
                board_size = int(query['boardSize'])
            target = 6 # Default
            if 'target' in query:
                target = int(query['target'])
            team1 = int(query['teamId1'])
            team2 = int(query['teamId2'])
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
    my_games = []
    for game in all_games.values():
        game_str = f"{game.player1}:{game.player2}:{game.team_symbol(game.whose_turn())}"
        current_game = {}
        current_game[game.game_id] = game_str
        my_games.append(current_game)
    resp["myGames"] = my_games

    return resp


def handle_get_my_teams(query):
    # Much simpler than the real server's implementation - will assume same teams
    resp = {}
    resp["code"] = "OK"
    my_teams = []
    team1 = {}
    team1[1338] = 'Team 1'
    team2 = {}
    team2[1361] = 'Team 1a'
    my_teams.append(team1)
    my_teams.append(team2)
    resp["myTeams"] = my_teams

    return resp


def handle_move(query):
    global move_id_counter
    query_type = query['type']

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

    game_id = int(query['gameId'])
    team_id = int(query['teamId'])

    print(f"query move={query['move']}")
    move_list = query['move'].split(',')
    move_x = int(move_list[0])
    move_y = int(move_list[1])

    row = move_x
    col = move_y
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
