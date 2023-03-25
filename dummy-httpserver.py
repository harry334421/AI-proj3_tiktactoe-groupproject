# -*- coding: utf-8; mode: python; tab-width: 4; indent-tabs-mode: nil -*-

# CSCI 6511: AI
# Project 3: Generalized Tic-Tac-Toe
# teamLHL
# - Patrick Husson
# - Hao Liu
# - Eric Luo
#
# April 19, 2023
#
# dummy_httpserver.py - HTTP server used for testing the client

from bottle import request,  route,  run
import json
import urllib.parse

mycount = 0

@route('<mypath:path>', method=['GET', 'POST'])
def query_handler( mypath ):
    global mycount
    mycount = mycount + 1
    print( f"count={mycount}")
    query = urllib.parse.parse_qs( request.query_string )
    if query[ 'type' ][ 0 ] == 'team':
        print( "Parsing the team command")
    elif query[ 'type' ][ 0 ] == 'myTeams':
        print( "Parsing the myTeams command" )
    resp = {}
    resp[ "code" ] = "OK"
    return json.dumps( resp )


if __name__ == "__main__":
    run( host='localhost', port=8080, debug=True )
