import random
import time
import numpy as np
from multiprocessing import Manager, Queue, Pool, cpu_count
import requests
import json

'''
Other Dependencies
'''
from TTTMoveMaker import move_worker, make_move
from TTTStrategy import TTTStrategy

class TTTAgent:
    #Constructor
    def __init__(self, board_size, target, opt, teamid1, teamid2, first, gameid=None, interval=5, evaluator=4, timeout=30, url="https://www.notexponential.com/aip2pgaming/api/index.php", headers='key.json'):
        self.board_size=board_size
        self.target=target
        self.url=url
        self.headers=self.get_header(headers)
        self.interval=interval
        self.teamid1=teamid1 
        self.teamid2=teamid2 
        self.first=first==1
        self.board=np.array([[0]*board_size for i in range(board_size)])
        self.opt=opt
        self.evaluator=evaluator
        self.status=False
        self.gameid=gameid
        self.ttt=TTTStrategy()
        self.timeout=timeout
        
        if opt==1:
            flag, gameid = self.start_game()
            if flag==True:
                print("Game started")
                print(f"Game ID (Tell the opponent team) {gameid}")
                self.gameid=gameid
                self.status=True
            else:
                print("Game failed to start. Check Intput.")
        elif opt==2:
            flag, board = self.get_board()
            #print(flag)
            if flag==True:
                print("Game confirmed.")
                self.board=board
                print("Current Board Status:")
                self.print_board()
                self.status=True
            else:
                print("Failed to join game. Check Intput.")
            
    #Get HTTP Header from File
    def get_header(self, file):
        return json.load(open(file,'r'))
    
    #Start Game
    def start_game(self):
        payload={'teamId1': f'{self.teamid1}','teamId2': f'{self.teamid2}','type': 'game','gameType': 'TTT','boardSize':f'{self.board_size}', 'target': f'{self.target}'} if self.first else {'teamId1': f'{self.teamid2}','teamId2': f'{self.teamid1}','type': 'game','gameType': 'TTT','boardSize':f'{self.board_size}', 'target': f'{self.target}'}
        response=requests.post(self.url, headers=self.headers, data=payload)
        response=response.json()
        if response['code']=='OK':
            return True, int(response['gameId'])
        else:
            return False, None
    
    #Get Board
    def get_board(self):
        response=requests.get(self.url+f"?type=boardString&gameId={self.gameid}", headers=self.headers)
        response=response.json()
        #print(response)
        if response['code']=='OK':
            return True, self.string_to_board(response['output'])
        else:
            return False, None        
    
    #String to NP Array 
    def string_to_board(self, boardstr):
        ele_dict={"X":-1, "O":1, "_":0, "-":0}
        rows=boardstr.split("\n")
        rows.remove("")
        if " " in rows[0]:
            board=np.array([[ele_dict[ele] for ele in row.split(" ")] for idx, row in enumerate(rows)])
        else:
            board=np.array([[ele_dict[ele] for ele in [*row]] for idx, row in enumerate(rows)])
        return board
    
    #Print Board
    def print_board(self):
        for row in self.board:
            print(" ".join(["X" if x == -1 else "O" if x == 1 else "_" for x in row]))
        print()
    
    #Get Moves 
    def get_moves(self):
        #print(self.url+f'?type=moves&gameId={self.gameid}&count=1')
        response=requests.get(self.url+f'?type=moves&gameId={self.gameid}&count=2', headers=self.headers)
        response=response.json()
        if response['code']=='OK':
            if len(response['moves'])==0:
                return True, None, None, []
            else:
                teamid=int(response['moves'][0]['teamId'])
                move=(int(response['moves'][0]['moveX']), int(response['moves'][0]['moveY']))
                if len(response['moves'])==2:
                    move1=(int(response['moves'][1]['moveX']), int(response['moves'][1]['moveY']))
                    return True, teamid, move, [move1, move]
                else:
                    return True, teamid, move, [move]
        else:
            return False, None, None, []
    
    #Post Move 
    def post_move(self, row, col):
        #print(f"Move posted @ row {row} col {col}")
        payload={'teamId': f'{self.teamid1}','move': f'{row},{col}','type': 'move','gameId': f'{self.gameid}'}
        #print(payload)
        response=requests.post(self.url, headers=self.headers, data=payload)
        response=response.json()
        #print(response)
        return response['code']=='OK'

    def play_game(self):
        _, teamid, _, last_moves = self.get_moves()
        first_move=True if teamid == None else False
        my_move=True if teamid == self.teamid2 else False
        if self.first==True:
            print("I am first mover")
        else:
            print("I am second mover")
        print("Last moves:", last_moves)
        while True:
            #If we are first mover
            if self.first==True:
                # Player 1 (Maximizing player)
                print(f'Player {"O"}')
                print(f"My round {my_move}")
                #Wait for Opponent Move
                if first_move==False & my_move==False:
                    print("First Mover Wait For Second Mover")
                    while not my_move:
                        success, teamid, move, last_moves = self.get_moves()
                        if success==True and teamid==self.teamid2:
                            print("X Player Made Move.")
                            my_move=True
                            #Get New Board 
                            _, self.board=self.get_board()
                            self.print_board()
                        else:
                            time.sleep(self.interval)
                #Start my round 
                print("Start my round (O)")
                #Make A Move
                row, col = make_move(self.board, True, self.target, last_moves, self.evaluator, self.timeout, self.ttt)
                self.board[row][col] = 1
                last_moves=[last_moves[-1], (row, col)] if len(last_moves)>0 else [(row, col)]
                first_move=False
                #Post Move
                self.post_move(row, col)
                _, self.board=self.get_board()
                #Set My Round to False 
                my_move=False
                self.print_board()
                winner = self.ttt.check_winner(self.board, self.target, row, col)
                if winner != 0 or self.ttt.is_full(self.board):
                    break
            #If we are second mover
            else:
                # Player 2 (Minimizing player)
                print(f'Player {"X"}')
                if first_move==True:
                    print("Second Mover Wait For First Mover's First Move")
                    while not my_move:
                        success, teamid, move, last_moves= self.get_moves()
                        if success==True and teamid is not None and teamid==self.teamid2:
                            print("O Player Made Move")
                            my_move=True
                            _, self.board=self.get_board()
                            self.print_board()
                        else:
                            time.sleep(self.interval)
                elif first_move==False & my_move==False:
                    print("Second Mover Wait For First Mover")
                    while not my_move:
                        success, teamid, move, last_moves= self.get_moves()
                        if success==True and teamid==self.teamid2:
                            print("O Player Made Move")
                            my_move=True
                            _, self.board=self.get_board()
                            self.print_board()
                        else:
                            time.sleep(self.interval)
                #Start My Round 
                print("Start my round (X)")
                row, col = make_move(self.board, False, self.target, last_moves, self.evaluator, self.timeout, self.ttt)
                self.board[row][col] = -1
                #Store Last moves
                last_moves=[last_moves[-1], (row, col)] if len(last_moves)>0 else [(row, col)]
                #Post Move 
                self.post_move(row, col)
                _, self.board=self.get_board()
                #Set My Round to False 
                my_move=False
                #Print Board 
                self.print_board()
                
                winner = self.ttt.check_winner(self.board, self.target, row, col)
                if winner != 0 or self.ttt.is_full(self.board):
                    break
        #print(winner)
        if winner == 1:
            print("Player 1 (Maximizing player) wins!")
        elif winner == -1:
            print("Player 2 (Minimizing player) wins!")
        else:
            print("It's a draw!")


if __name__=='__main__':
    #Start 
    print("TTT Agent Program Starts.")
    '''
    #Old codes to request input from teriminal
    #Options for start or join a game
    opt=None
    while opt not in [1,2]:
        try:
            print("Options to start the agent:\n 1. Start a new game\n 2. Join a game")
            opt=int(input("Choice: >"))
        except:
            print("Invalid input")
    if opt==2:
        gameid=int(input("What is the gameId? "))
    else:
        gameid=None
    #Team IDs
    teamid1=int(input("Team ID of the My Team:"))
    teamid2=int(input("Team ID of the Opponent Team:"))
    #First Mover
    first=None
    while first not in [1,2]:
        try:
            print("Who is the first mover? \n 1. Our Team\n 2. Opponent Team?")
            first=int(input("Choice: >"))
        except:
            print("Invalid input.")
    #Board Size and Target
    board_size=0
    while board_size<3:
        try:
            board_size=int(input("What is the board size?  >"))
        except:
            print("Invalid input.")
    target=0
    while target<3:
        try:
            target=int(input("What is the target number?  >"))
        except:
            print("Invalid input.")
    '''
    
    while True:
        try:
            gamefile = input("Name of the game setup JSON file: >")
            game_dict=json.load(open(gamefile, 'r'))
            opt=game_dict['Game Option']
            gameid=game_dict['Game ID']
            board_size=game_dict['Game Parameters']['Board Size']
            target=game_dict['Game Parameters']['Target']
            first=game_dict['Game Parameters']['First Mover']
            teamid1=game_dict['Teams']['Team 1']
            teamid2=game_dict['Teams']['Team 2']
            evaluator=game_dict['Evaluator']    
            break
        except:
            print("Something wrong with the game setup file. Try Again")
            continue
    
    #Agent Starts 
    tttagent=TTTAgent(board_size, target, opt, teamid1, teamid2, first, gameid=gameid, evaluator=evaluator)
    if tttagent.status==True:
        tttagent.play_game()
    else:
        print("Agent did not start correctly. Check input and try again.")