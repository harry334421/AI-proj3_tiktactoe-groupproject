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
# project_httpclient.py - HTTP client side of the game (our side)


import ast
import requests
import urllib.parse


# Using the default requests user agent caused errors with the class server:
# 'Not Acceptable! An appropriate representation of the requested resource could
# not be found on this server.'
my_key = 0
my_id = 0

use_dummy = True
dummy_id = '9999'
dummy_ua = 'Mozilla/5.0 (X11; Linux x86_64; rv:102.0) Gecko/20100101 Firefox/102.0'
dummy_http_server = 'http://127.0.0.1:8080'

real_http_server = 'https://www.notexponential.com/aip2pgaming/api/index.php'


my_games = {}

def create_new_game(board_size, target_size):
    # TODO - Temporary - just going to hardcode some things for now
    # - Client will be Player 1, Server will be Player 2

    params = {}
    params['type'] = 'game'
    params['teamId1'] = my_id
    params['teamId2'] = dummy_id # TODO - Check if using dummy eventually...
    params['gameType'] = 'TTT'
    params['boardSize'] = board_size
    params['target'] = target_size

    query = urllib.parse.urlencode(params)
    url = f"{dummy_http_server}?{query}"

    payload={}
    headers = {
        'x-api-key': my_key,
        'userid': my_id,
        'User-Agent': dummy_ua
    }

    raw_response = requests.request("POST", url, headers=headers, data=payload)
    response = ast.literal_eval(raw_response.text)

    if ( response['code'] == 'OK'):
        print(f"Created game {response['gameId']} successfully")
    else:
        print(f"Failure in creating game,  message={response['message']}")


def get_my_games():
    params = {}
    params['type'] = 'myGames'

    query = urllib.parse.urlencode(params)
    url = f"{dummy_http_server}?{query}"

    payload={}
    headers = {
        'x-api-key': my_key,
        'userid': my_id,
        'User-Agent': dummy_ua
    }

    raw_response = requests.request("GET", url, headers=headers, data=payload)
    response = ast.literal_eval(raw_response.text)
    if ( response['code'] == 'OK'):
        my_games = response['games']
        print(f"my_games={my_games}")
    else:
        print(f"Failure in creating game,  message={response['message']}")

    return my_games


def get_game_board(game_id):
    params = {}
    params['type'] = 'boardString'
    params['gameId'] = game_id

    query = urllib.parse.urlencode(params)
    url = f"{dummy_http_server}?{query}"

    payload={}
    headers = {
        'x-api-key': my_key,
        'userid': my_id,
        'User-Agent': dummy_ua
    }

    raw_response = requests.request("GET", url, headers=headers, data=payload)
    response = ast.literal_eval(raw_response.text)
    if ( response['code'] == 'OK'):
        board = response['output']
    else:
        print(f"Failure in getting board for {game_id},  message={response['message']}")

    return board


def demo():
    # Create a few new games
    board_size = 3
    target_size = 3
    create_new_game(board_size,  target_size)

    board_size += 1
    create_new_game(board_size,  target_size)

    # Make sure the server sees them
    my_games = get_my_games()

    # Show the boards (the reason why we changed the sizes earlier)
    for game_id in my_games:
        board = get_game_board(game_id)
        print(f"Board {game_id}:")
        print(board)

if __name__ == '__main__':
    # Make sure API key and user ID are in memory
    with open('token.txt') as f:
        for line in f:
            if not line.startswith("#"):
                values = line.split(',')
                my_id = values[0]
                my_key = values[1].strip()
                break

    demo()


