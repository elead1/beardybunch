__author__ = 'Eric'

import Networking.Message
import Networking.MessagingInterface as MessagingInterface
import socket
import threading
from time import sleep

def thread_method(name, q):
    sock = socket.socket()
    sock.connect(('127.0.0.1', 5555))
    msg = Networking.Message()
    msg.set_type('HELLO')
    msg.set_params({'message': 'hi from' + name})
    sock.send(msg.encode_message())

    resp = sock.recv(1024)
    q.put(resp)

class client(MessagingInterface):
    def __init__(self):
        self._threads = []
        self._response_q = threading.Queue()

        self.spawn_threads()

        while self._threads.active_count() < 1:
            sleep(1)

        while not self._response_q.empty():
            print(self._response_q.get())

    def spawn_threads(self):
        for i in range(6):
            self._threads.append(threading.Thread(target=thread_method, args=('Thread'+str(i), self._response_q)))
        for t in self._threads:
            t.start()