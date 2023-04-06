# Project 3 Skeleton

This is an attempt to create a solid frame for the Tic-Tac-Toe game that allows it to interact with other engines.

## Packages required

- bottle
- json
- urllib

## Running Just the Game Logic

The game logic is in a separate file (mostly for now). You can adjust the board size and have it play against itself

```
    python3 V9-MinMax+PatternSeeking-TTT-.py
```

## Running

First, copy your user id and API key into `token_TEMPLATE.txt` and save as `token.txt`.

### Using the Class Server

No arguments are needed for the single program used:

```
    python3 project3.py
```

### Using the Dummy Server

It may make sense to do some testing against the dummy server for speed purposes and to improve debugging speed.

Two separate terminal windows are needed.

For the server (start it first):

```
    python3 dummy-httpserver.py
```


Now, in the other window, start the client. Please note that you should add the '-d' option when running against the dummy server.

```
    python3 project3.py -d
```

## TODOs

- Integrate Eric's logic into separate strategy files
- Get all commands working against the real server

## Troubleshooting

Some problems can be resolved pretty quickly.

### Bad URL

If you get an error like the following,  make sure you begin with `http://` for the URL string:

```
    requests.exceptions.InvalidSchema: No connection adapters were found for '127.0.0.1:8080'
```
