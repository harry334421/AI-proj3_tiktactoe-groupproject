# CSCI 6511 Project 3

Project 3 creates a generalized Tic-Tac-Toe game interacts with other engines via a dummy server or via the class server.

## Packages required

- bottle
- json
- urllib

## Running

First, copy your user id and API key into `key-TEMPLATE.json` and save as `key.json`. Also, update your copy of `settings.json` to use your desired evaluator.

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

## Changelog

A [changelog](CHANGELOG.md) details some of the development process.

## Troubleshooting

Some problems can be resolved pretty quickly.

### Bad URL

If you get an error like the following,  make sure you begin with `http://` for the URL string:

```
    requests.exceptions.InvalidSchema: No connection adapters were found for '127.0.0.1:8080'
```
