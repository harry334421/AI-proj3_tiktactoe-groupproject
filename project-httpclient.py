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
dummy_ua = 'Mozilla/5.0 (X11; Linux x86_64; rv:102.0) Gecko/20100101 Firefox/102.0'

if __name__ == '__main__':

    # Make sure API key and user ID are in memory
    my_id = 0
    my_key = 0
    with open( 'token.txt' ) as f:
        for line in f:
            if not line.startswith( "#" ):
                values = line.split( ',' )
                my_id = values[ 0 ]
                my_key = values[ 1 ].strip()
                break

    #http_server = "https://www.notexponential.com/aip2pgaming/api/index.php
    http_server = 'http://127.0.0.1:8080'

    params = {}
    # Message 1
    #params[ 'type' ] = 'myTeams'
    # Message 2
    params[ 'type' ] = 'team'
    params[ 'teamId' ] = '1338'
    # ...

    query = urllib.parse.urlencode( params )
    url = f"{http_server}?{query}"

    payload={}
    headers = {
        'x-api-key': my_key,
        'userid': my_id,
        'User-Agent': dummy_ua
    }
    payload={}

    # Just replace "GET" with "POST" as necessary
    response = requests.request( "GET", url, headers=headers, data=payload )

    print( response.text )
    mydict = ast.literal_eval( response.text )
    print(f"Response as JSON:{mydict}")
