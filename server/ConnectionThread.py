import socket
import threading
import logging
import Networking.Message as Message
__author__ = 'Eric'

'''Processes communications to/from one connected client. Ensures received data is a proper message as expected.'''

class ConnectionThread(threading.Thread):

    def __init__(self, manager, client_sock):
        self._socket = client_sock
        self._manager = manager

    def run(self):
        while True:
            data = self._socket.recv(1024)
            if not data:
                continue
            try:
                msg = Message(data)
                self._manager.on_message_received(msg)
            except ValueError as ve:
                logging.info("Data received was not proper JSON string.")