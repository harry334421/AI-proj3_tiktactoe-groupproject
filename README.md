# HTTP Server-Client Example

This is an attempt to create a solid frame for the Tic-Tac-Toe game that allows it to interact with other engines.

## Packages required

- bottle
- json
- urllib

## Running the Game Logic

The game logic is in a separate file (mostly for now). You can adjust the board size and have it play against itself

```
    python3 V9-MinMax+PatternSeeking-TTT-.py
```

## Running the Server/Client

First, copy your user id and API key into `token_TEMPLATE.txt` and save as `token.txt`.

Now, run in two separate terminal windows.

For the server (start it first):

```
    python3 dummy-httpserver.py
```

For the client:

```
    python3 project3.py
```

## TODOs

- Integrate Eric's logic into separate strategy files
- Test commands against real server
- ...

## Troubleshooting

Some problems can be resolved pretty quickly.

### Bad URL

If you get an error like the following,  make sure you begin with `http://` for the URL string:

```
    requests.exceptions.InvalidSchema: No connection adapters were found for '127.0.0.1:8080'
```




#Eric's change log 2023.04.06
1. Repackaged all strategy related functions into Class TTTStrategy in TTTStrategy.py 
2. Move maker functions and the parallel worker is now in TTTMoveMaker.py
3. the project_httpclient.py is now repackaged into TTTAgent.py 
    a. TTTAgent now handles all communication with the server 
    b. TTTAgent calls move maker to make moves and then post it back to the server 
    c. TTTAgent now reads a game setup file (e.g. game-TEMPLATE.json) to start the agent game-TEMPLATE.json has comment in it 
    d. TTTAgent also reads the header file (e.g. key-TEMPLATE.json) to store info on the HTTP header info, the default file header file name is key.json.
##Eric's change log 2023.04.06 - v2 
4. Parallelized pattern check codes and packaged them into a method for TTTStrategy now.