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

dummy_http_server = 'http://127.0.0.1:8080'
real_http_server = 'https://www.notexponential.com/aip2pgaming/api/index.php'

class ProjectHttpClient:
    # Constructor
    # my_id: Team ID of client (us)
    # api_key: Required API key (necessary for using class server)
    # play_dummy_server: True if playing the dummy server, False if playing the real server
    def __init__(self, header_file,  play_dummy_server):
        self.my_games = {}
        self.header = json.load(open(header_file,'r'))
        self.my_user_id = int(self.header['userId'])
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
        my_teams = []
        raw_response = requests.get(url, headers=self.header, data=payload)
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
        payload = {}
        payload['type'] = 'game'
        payload['gameType'] = 'TTT'
        payload['boardSize'] = board_size
        payload['target'] = target_size
        payload['teamId1'] = team1_id
        payload['teamId2'] = team2_id

        raw_response = requests.post(self.server_url, headers=self.header, data=payload,  files=[])
        try:
            response = json.loads(raw_response.text)
        except:
            print(f"Server game non-JSON response: {raw_response.text}")
            return

        if ( response['code'] == 'OK'):
            print(f"Created game {response['gameId']} successfully")
        else:
            if 'message' in response:
                print(f"Failure in creating game, message={response['message']}")
            else:
                print("Failure with no message given")

    def get_my_games(self):
        params = {}
        params['type'] = 'myOpenGames'

        query = urllib.parse.urlencode(params)
        url = f"{self.server_url}?{query}"

        payload={}
        my_games = []
        raw_response = requests.get(url, headers=self.header, data=payload)
        try:
            response = json.loads(raw_response.text)
        except:
            print(f"Server game non-JSON response: {raw_response.text}")
            return my_games

        if ( response['code'] == 'OK'):
            my_games = response['myGames']
        else:
            if 'message' in response:
                print(f"Failure in getting games, message={response['message']}")
            else:
                print("Failure with no message given")

        return my_games


    def get_game_map(self, game_id):
        params = {}
        params['type'] = 'boardMap'
        params['gameId'] = game_id

        query = urllib.parse.urlencode(params)
        url = f"{self.server_url}?{query}"

        payload={}
        board_map = []
        target = -1
        raw_response = requests.get(url, headers=self.header, data=payload)
        try:
            response = json.loads(raw_response.text)
        except:
            print(f"Server game non-JSON response: {raw_response.text}")
            return board_map

        print(response)
        if ( response['code'] == 'OK'):
            board_map = response['output']
            target = int(response['target'])
        else:
            if 'message' in response:
                print(f"Failure in getting map for {game_id}, message={response['message']}")
            else:
                print(f"Failure with no message given for getting map for {game_id}")

        return board_map, target

    def get_game_board(self, game_id):
        params = {}
        params['type'] = 'boardString'
        params['gameId'] = game_id

        query = urllib.parse.urlencode(params)
        url = f"{self.server_url}?{query}"

        payload={}

        board = ""
        target = -1
        raw_response = requests.get(url, headers=self.header, data=payload)
        try:
            response = json.loads(raw_response.text)
        except:
            print(f"Server game non-JSON response: {raw_response.text}")
            return board

        print(response)
        if ( response['code'] == 'OK'):
            board = response['output']
            target = int(response['target'])
        else:
            if 'message' in response:
                print(f"Failure in getting board for {game_id}, message={response['message']}")
            else:
                print(f"Failure with no message given for getting board for {game_id}")

        return board, target


    def make_move(self, game_id, team_id, row, col):
        payload = {}
        payload['type'] = 'move'
        payload['gameId'] = game_id
        # Server marks moves as (x,y) but acts backwards if (col,row) given
        payload['move'] = f"{row},{col}"
        payload['teamId'] = team_id

        raw_response = requests.post(self.server_url, headers=self.header, data=payload, files=[])
        try:
            response = json.loads(raw_response.text)
        except:
            print(f"Server game non-JSON response: {raw_response.text}")
            return

        if not response['code'] == 'OK':
            if 'message' in response:
                print(f"Failure in making move, message={response['message']}")
            else:
                print("Failure in making move with no message given")


    def get_moves(self, game_id, n_moves,  quiet=False):
        params = {}
        params['type'] = 'moves'
        params['gameId'] = game_id
        params['count'] = n_moves

        query = urllib.parse.urlencode(params)
        url = f"{self.server_url}?{query}"

        payload={}
        moves = [] # Empty for error checking
        raw_response = requests.get(url, headers=self.header, data=payload)
        try:
            response = json.loads(raw_response.text)
        except:
            print(f"Server game non-JSON response: {raw_response.text}")
            return moves

        if ( response['code'] == 'OK'):
            if 'moves' in response:
                moves = response['moves']
        else:
            if not quiet:
                if 'message' in response:
                    print(f"Failure in getting moves for {game_id}, message={response['message']}")
                else:
                    print(f"Failure with no message given for getting moves for {game_id}")

        return moves

