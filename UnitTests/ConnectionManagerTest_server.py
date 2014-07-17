__author__ = 'Eric'

import Networking.Message
import Networking.MessagingInterface
import server.ConnectionManager.ConnectionManager as ConnectionManager

class Server(Networking.MessagingInterface):
    def __init__(self):
        self._connectionmanager = ConnectionManager(5555)

        self._connectionmanager.add_connection_listener(self)

    def send_message(self, message):
        self._connectionmanager.send_message(message)

    def receive_message(self, message):
        print(message)
        response = Networking.Message()
        response.set_type('HELLO')
        response.set_params({'message': 'hi from server'})
        self.send_message(response)