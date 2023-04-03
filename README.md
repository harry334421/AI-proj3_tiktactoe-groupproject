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

For the server:

```
    python3 dummy-httpserver.py
```

For the client:

```
    python3
    >>> exec(open("example_game.py").read())
    # Now make moves using phc.make_move(game_id,row,col)
    phc.make_move(2000,0,0)
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
