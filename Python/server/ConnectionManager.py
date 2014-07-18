import socket
import threading
import hashlib
from server.ConnectionThread import ConnectionThread

__author__ = 'Eric'

'''Handles connections to clients for a particular game. This includes message passing, keep-alives,
and waiting for connections for game start.'''

class ConnectionManager:

    '''Port is the TCP port number to listen on.'''
    def __init__(self, port):
        self._connection_listeners = []
        #Keyed by client_id
        self._client_threads = {}
        self._comm_port = port
        self._listen_socket = socket.socket()

        self._listen_socket.bind(('', port))

        listen_thread = threading.Thread(group=None, target=self.add_client_thread)
        listen_thread.start()

    '''Adds a listener to receive messages/callbacks from this ConnectionManager'''
    def add_connection_listener(self, listener):
        self._connection_listeners.append(listener)

    def add_client_thread(self):
        self._listen_socket.listen(0)
        while len(self._client_threads.keys()) < 6:
            conn, addr = self._listen_socket.accept()
            client_id = self.gen_client_id(addr)
            self._client_threads[client_id] = ConnectionThread(self, conn)
            self._client_threads[client_id].start()
            self._client_threads[client_id].name = str(client_id)
        #work on logic for handling number of connections/connection timeout

    def on_message_received(self, message):
        for listener in self._connection_listeners:
            listener.receive_message(message)

    def send_message(self, message):
        for i in range(len(self._client_threads.keys())):
            self._client_threads[list(self._client_threads)[i]].send(message)

    '''client_id is the hex representation of the md5 hash of the IP address + port'''
    def gen_client_id(self, address_tuple):
        return hashlib.md5(bytearray(address_tuple[0] + str(address_tuple[1]), 'utf_8')).hexdigest()