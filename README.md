# HTTP Server-Client Example

This is an attempt to create a solid frame for the Tic-Tac-Toe game that allows it to interact with other engines.

## Packages required

- bottle
- json
- urllib

## Running the Server/Client

First, copy your user id and API key into `token_TEMPLATE.txt` and save as `token.txt`.

Now, run in two separate terminal windows.

For the server:

```
    python3 dummy-httpserver.py
```

For the client:

```
    python3 project-httpclient.py http://127.0.0.1:8080
```

## Troubleshooting

Some problems can be resolved pretty quickly.

### Bad URL

If you get an error like the following,  make sure you begin with `http://` for the URL string:

```
    requests.exceptions.InvalidSchema: No connection adapters were found for '127.0.0.1:8080'
```
