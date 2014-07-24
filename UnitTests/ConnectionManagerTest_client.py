__author__ = 'Eric'

from Networking.Message import Message
from Networking.MessagingInterface import MessagingInterface
import socket
import threading
import queue
from time import sleep

def thread_method(name, q):
    sock = socket.socket()
    sock.connect(('127.0.0.1', 5555))
    msg = Message()
    msg.set_type('HELLO')
    msg.set_params({'message': 'hi from ' + name})
    sock.send(bytearray(msg.encode_message(), 'utf_8'))

    resp = sock.recv(1024)
    sleep(5)
    q.put(str(resp, 'utf_8'))

class client(MessagingInterface):
    def __init__(self):
        self._threads = []
        self._response_q = queue.Queue()

        self.spawn_threads()

        while threading.active_count() < 1:
            sleep(1)

        while not self._response_q.empty():
            print(Message(self._response_q.get()).encode_message())
        #sock = socket.socket()
        #sock.connect(('127.0.0.1', 5555))

    def spawn_threads(self):
        for i in range(6):
            self._threads.append(threading.Thread(target=thread_method, args=('Thread'+str(i), self._response_q)))
        for t in self._threads:
            t.start()

if __name__ == '__main__':
    c = client()