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


import json
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
    # play_dummy_server: True if playing the dummy server, False if playing the real server
    def __init__(self, my_id,  api_key,  play_dummy_server):
        self.my_games = {}
        self.my_id = my_id
        self.api_key = api_key
        self.ua = fake_ua
        if play_dummy_server:
            self.server_url = dummy_http_server
        else:
           self.server_url = real_http_server

        # Getting teams from the server just to be sure we can make moves
        self.teams = self.get_my_teams()

    def get_my_teams(self):
        params = {}
        params['type'] = 'myTeams'

        query = urllib.parse.urlencode(params)
        url = f"{self.server_url}?{query}"

        payload={}
        headers = {
            'x-api-key': self.api_key,
            'userid': self.my_id,
            'User-Agent': self.ua
        }

        my_teams = []
        raw_response = requests.request("GET", url, headers=headers, data=payload)
        try:
            response = json.loads(raw_response.text)
        except:
            print(f"Server game non-JSON response: {raw_response.text}")
            return my_teams

        if ( response['code'] == 'OK'):
            # The myTeams response is a list of maps
            for team_map in response['myTeams']:
                for team_id in team_map.keys():
                    my_teams.append(int(team_id))

        return my_teams


    def create_new_game(self, board_size, target_size, team1_id, team2_id):
        params = {}
        params['type'] = 'game'
        params['gameType'] = 'TTT'
        params['boardSize'] = board_size
        params['target'] = target_size
        params['teamId1'] = team1_id
        params['teamId2'] = team2_id

        query = urllib.parse.urlencode(params)
        url = f"{self.server_url}?{query}"

        payload={}
        headers = {
            'x-api-key': self.api_key,
            'userid': self.my_id,
            'User-Agent': self.ua
        }

        raw_response = requests.request("POST", url, headers=headers, data=payload)
        try:
            response = json.loads(raw_response.text)
        except:
            print(f"Server game non-JSON response: {raw_response.text}")
            return

        if ( response['code'] == 'OK'):
            print(f"Created game {response['gameId']} successfully")
        else:
            print(f"Failure in creating game, message={response['message']}")


    def get_my_games(self):
        params = {}
        params['type'] = 'myOpenGames'

        query = urllib.parse.urlencode(params)
        url = f"{self.server_url}?{query}"

        payload={}
        headers = {
            'x-api-key': self.api_key,
            'userid': self.my_id,
            'User-Agent': self.ua
        }

        my_games = []
        raw_response = requests.request("GET", url, headers=headers, data=payload)
        try:
            response = json.loads(raw_response.text)
        except:
            print(f"Server game non-JSON response: {raw_response.text}")
            return my_games

        if ( response['code'] == 'OK'):
            my_games = response['myGames']
        else:
            print(f"Failure in creating game,  message={response['message']}")

        return my_games


    def get_game_map(self, game_id):
        params = {}
        params['type'] = 'boardMap'
        params['gameId'] = game_id

        query = urllib.parse.urlencode(params)
        url = f"{self.server_url}?{query}"

        payload={}
        headers = {
            'x-api-key': self.api_key,
            'userid': self.my_id,
            'User-Agent': self.ua
        }

        board_map = []
        raw_response = requests.request("GET", url, headers=headers, data=payload)
        try:
            response = json.loads(raw_response.text)
        except:
            print(f"Server game non-JSON response: {raw_response.text}")
            return board_map

        if ( response['code'] == 'OK'):
            board_map = response['output']
        else:
            print(f"Failure in getting board for {game_id},  message={response['message']}")

        return board_map

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

        board = ""
        raw_response = requests.request("GET", url, headers=headers, data=payload)
        try:
            response = json.loads(raw_response.text)
        except:
            print(f"Server game non-JSON response: {raw_response.text}")
            return board

        if ( response['code'] == 'OK'):
            board = response['output']
        else:
            print(f"Failure in getting board for {game_id},  message={response['message']}")

        return board


    def make_move(self, game_id, team_id, row, col):
        params = {}
        params['type'] = 'move'
        params['gameId'] = game_id
        params['move'] = f"{col},{row}" # Column is x coordinate and row is y coordinate
        params['teamId'] = team_id

        query = urllib.parse.urlencode(params)
        url = f"{self.server_url}?{query}"

        payload={}
        headers = {
            'x-api-key': self.api_key,
            'userid': self.my_id,
            'User-Agent': self.ua
        }

        raw_response = requests.request("POST", url, headers=headers, data=payload)
        try:
            response = json.loads(raw_response.text)
        except:
            print(f"Server game non-JSON response: {raw_response.text}")
            return

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

        moves = [] # Empty for error checking

        raw_response = requests.request("GET", url, headers=headers, data=payload)
        try:
            response = json.loads(raw_response.text)
        except:
            print(f"Server game non-JSON response: {raw_response.text}")
            return moves
        print(f"raw_response.text={raw_response.text}")

        if ( response['code'] == 'OK'):
            moves = response['moves']
        else:
            print(f"Failure in making move, message={response['message']}")

        return moves

