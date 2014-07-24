import SocketServer
import threading
import hashlib
from time import sleep

__author__ = 'Eric'
'''Handles connections to clients for a particular game. This includes message passing and waiting for connections for
game start.'''


class ConnectionHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        connection_listeners.append(self.request)


class ConnectionServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    '''Override default behavior of TCPServer's shutdown_request to keep connections alive.'''
    def shutdown_request(self, request):
        pass


class ConnectionManager:
    '''Port is the TCP port number to listen on.'''
    def __init__(self, game_manager, port):
        self._game = game_manager
        connection_listeners = []
        self._bind_addr = ('', port)
        #Keyed by client_id

        self._server = ConnectionServer(self._bind_addr, ConnectionHandler)

        self._server_thread = threading.Thread(self._server.serve_forever)
