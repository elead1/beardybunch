__author__ = 'Eric'

from Networking.Message import Message
from Networking.MessagingInterface import MessagingInterface
from server.ConnectionManager import ConnectionManager
from time import sleep

class Server(MessagingInterface):
    def __init__(self):
        self._connectionmanager = ConnectionManager(5555)

        self._connectionmanager.add_connection_listener(self)
        responses_received = 0
        while responses_received != 6:
            sleep(1)

    def send_message(self, message):
        self._connectionmanager.send_message(message)

    def receive_message(self, message):
        print(message.encode_message())
        response = Message()
        response.set_type('HELLO')
        response.set_params({'message': 'hi from server'})
        self.send_message(response)

if __name__ == '__main__':
    s = Server()
