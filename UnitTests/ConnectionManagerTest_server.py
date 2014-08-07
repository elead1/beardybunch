from Networking.Server import Server
from time import sleep

__author__ = 'Eric'


pings_recvd = 0
num_cli = 1

class ServerTester():
    def __init__(self):
        pass

    def notify_put(self, q):
        global pings_recvd
        received = q.get()
        sender = received['sender']
        msg = received['message'].decode()
        sock = received['socket']
        print "Received payload from ", repr(sender)
        print "Payload: (" + msg + ")"
        sock.sendall("Server's response!".encode())


if __name__ == '__main__':
    s = ServerTester()
    serv = Server(5555, s)
    serv.start_server()
    while serv.get_clients() > 0:
        num_cli = len(serv.get_clients())
        sleep(0.5)
    serv.stop_server()