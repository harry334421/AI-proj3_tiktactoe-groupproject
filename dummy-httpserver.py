#!/usr/bin/env python

from http.server import BaseHTTPRequestHandler, HTTPServer
import os

#Create custom HTTPRequestHandler class
class DummyHTTPRequestHandler(BaseHTTPRequestHandler):

    # def __init__():
    #   self.model = model( ...parameters... )

    # TODO - Handle GET and POST commands, pass required data to model

    # Handle GET command
    def do_GET(self):
        rootdir = './' # file location
        try:
            if self.path.endswith('.html'):
                f = open(rootdir + self.path,encoding='utf-8') #open requested file

                #send code 200 response
                self.send_response(200)

                #send header first
                self.send_header('Content-type','text-html; charset=utf-8')
                self.end_headers()

                #send file content to client
                # (and make sure they are bytes-like objects)
                self.wfile.write(f.read().encode())
                f.close()
                return

        except IOError:
            self.send_error(404, 'file not found')

def run():
    print('http server is starting...')

    #ip and port of servr
    #by default http server port is 80
    #server_address = ('127.0.0.1', 80)
    # Using a larger port number to get around system permissions
    server_address = ('127.0.0.1',8080)
    httpd = HTTPServer(server_address, DummyHTTPRequestHandler)
    print('http server is running...')
    httpd.serve_forever()

if __name__ == '__main__':
    run()
