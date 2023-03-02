#!/usr/bin/env python

import requests
import sys

if __name__ == '__main__':

    #get http server ip
    http_server = sys.argv[1]

    # Create model
    #model = model( ...parameters... )

    # Initialize game
    # If we are team 1, we go first with 'X' (?)
    # If we are team 2, we go second with 'O' (?)
    # requests.post( ... )

    # If we went first, make a move
    # ...

    # Will become something like 'while !model.in_end_state():' ?
    while True:

        # Will we need to get the board state and list of moves each time?
        # ...

        # Just something to demonstrate that server is communicating
        myinput = input('input GET command (ex. dummy.html): ')
        myinput = myinput.split()

        if myinput[0] == 'exit': #type exit to end it
            break

        url = f"{http_server}/{myinput[0]}"
        rg = requests.get( url )

        print( rg.text )
