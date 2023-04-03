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
fake_ua = 'Mozilla/5.0 (X11; Linux x86_64; rv:102.0) Gecko/20100101 Firefox/102.0'

dummy_http_server = 'http://127.0.0.1:8080'
real_http_server = 'https://www.notexponential.com/aip2pgaming/api/index.php'

class ProjectHttpClient:
    # Constructor
    # my_id: Team ID of client (us)
    # api_key: Required API key (necessary for using class server)
    # play_real_server: True if playing the real server, False if playing the dummy server
    def __init__(self, my_id,  api_key,  play_real_server):
        self.my_games = {}
        self.my_id = my_id
        self.api_key = api_key
        self.ua = fake_ua
        if play_real_server:
            self.server_url = real_http_server
        else:
           self.server_url = dummy_http_server


    def create_new_game(self, board_size, target_size,  opponent_id, me_first):
        params = {}
        params['type'] = 'game'
        params['gameType'] = 'TTT'
        params['boardSize'] = board_size
        params['target'] = target_size

        if me_first:
            params['teamId1'] = self.my_id
            params['teamId2'] = opponent_id
        else:
            params['teamId1'] = opponent_id
            params['teamId2'] = self.my_id

        query = urllib.parse.urlencode(params)
        url = f"{self.server_url}?{query}"

        payload={}
        headers = {
            'x-api-key': self.api_key,
            'userid': self.my_id,
            'User-Agent': self.ua
        }

        raw_response = requests.request("POST", url, headers=headers, data=payload)
        response = ast.literal_eval(raw_response.text)

        if ( response['code'] == 'OK'):
            print(f"Created game {response['gameId']} successfully")
        else:
            print(f"Failure in creating game,  message={response['message']}")


    def get_my_games(self):
        params = {}
        params['type'] = 'myGames'

        query = urllib.parse.urlencode(params)
        url = f"{self.server_url}?{query}"

        payload={}
        headers = {
            'x-api-key': self.api_key,
            'userid': self.my_id,
            'User-Agent': self.ua
        }

        raw_response = requests.request("GET", url, headers=headers, data=payload)
        response = ast.literal_eval(raw_response.text)
        if ( response['code'] == 'OK'):
            my_games = response['games']
            print(f"my_games={my_games}")
        else:
            print(f"Failure in creating game,  message={response['message']}")

        return my_games


    def get_game_board(self, game_id):
        params = {}
        params['type'] = 'boardString'
        params['gameId'] = game_id

        query = urllib.parse.urlencode(params)
        url = f"{self.server_url}?{query}"

        payload={}
        headers = {
            'x-api-key': self.api_key,
            'userid': self.my_id,
            'User-Agent': self.ua
        }

        raw_response = requests.request("GET", url, headers=headers, data=payload)
        response = ast.literal_eval(raw_response.text)
        if ( response['code'] == 'OK'):
            board = response['output']
        else:
            print(f"Failure in getting board for {game_id},  message={response['message']}")

        return board


    def make_move(self, game_id,  row,  col):
        params = {}
        params['type'] = 'move'
        params['gameId'] = game_id
        params['teamId'] = self.my_id
        params['move'] = f"{col},{row}" # Column is x coordinate and row is y coordinate

        query = urllib.parse.urlencode(params)
        url = f"{self.server_url}?{query}"

        payload={}
        headers = {
            'x-api-key': self.api_key,
            'userid': self.my_id,
            'User-Agent': self.ua
        }

        raw_response = requests.request("POST", url, headers=headers, data=payload)
        response = ast.literal_eval(raw_response.text)
        if not response['code'] == 'OK':
            print(f"Failure in making move, message={response['message']}")


    def get_moves(self, game_id, n_moves):
        params = {}
        params['type'] = 'moves'
        params['gameId'] = game_id
        params['count'] = n_moves

        query = urllib.parse.urlencode(params)
        url = f"{self.server_url}?{query}"

        payload={}
        headers = {
            'x-api-key': self.api_key,
            'userid': self.my_id,
            'User-Agent': self.ua
        }

        raw_response = requests.request("GET", url, headers=headers, data=payload)
        response = ast.literal_eval(raw_response.text)
        moves = [] # Empty for error checking
        if ( response['code'] == 'OK'):
            moves = response['moves']
        else:
            print(f"Failure in making move, message={response['message']}")

        return moves



if __name__ == '__main__':
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
    # Create a few new games
    board_size = 3
    target_size = 3
    me_first = True
    phc.create_new_game(board_size,  target_size,  9999,  me_first)

    board_size += 1
    me_first = False
    phc.create_new_game(board_size,  target_size, 9999,   me_first)

    # Make sure the server sees them
    my_games = phc.get_my_games()

    # Show the boards (the reason why we changed the sizes earlier)
    for game_id in my_games:
        board = phc.get_game_board(game_id)
        print(f"Board {game_id}:")
        print(board)

