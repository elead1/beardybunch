import socket
import threading
import logging
from Networking.Message import Message
__author__ = 'Eric'

'''Processes communications to/from one connected client. Ensures received data is a proper message as expected.'''

class ConnectionThread(threading.Thread):

    def __init__(self, manager, client_sock, name=None):
        threading.Thread.__init__(self, name=name)
        self._socket = client_sock
        self._manager = manager
        self.name = name
    def run(self):
        while True:
            data = self._socket.recv(1024)
            if not data:
                continue
            try:
                msg = Message(str(data, 'utf_8'))
                self._manager.on_message_received(msg)
            except ValueError as ve:
                logging.info("Data received was not proper JSON string.")

    def send(self, message):
        self._socket.send(bytearray(message.encode_message(), 'utf_8'))