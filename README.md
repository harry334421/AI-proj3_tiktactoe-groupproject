# HTTP Server-Client Example / Model Example

Adapted from some python 2.7 code:
https://www.godo.dev/tutorials/python-http-server-client/

## Packages required

I needed to install the python3-httpbin package on my computer to get access to the HTTP server handlers. I also installed the requests package for making the API calls.

## Running the Server/Client

Run in two separate terminal windows.

For the server:

```
    python3 dummy-httpserver.py
```

For the client:

```
    python3 project-httpclient.py http://127.0.0.1:8080
```

## Running the MVC

This example is adapted from `https://www.tutorialspoint.com/python_design_patterns/python_design_patterns_model_view_controller.htm`. It is probably overkill to follow this pattern since the interactions between the server and client follow a tight script.

The controller is the main class.

```
    python3 controller.py
```

## Troubleshooting

Some problems can be resolved pretty quickly.

### Bad URL

If you get an error like the following,  make sure you begin with `http://` for the URL string:

```
    requests.exceptions.InvalidSchema: No connection adapters were found for '127.0.0.1:8080'
```
