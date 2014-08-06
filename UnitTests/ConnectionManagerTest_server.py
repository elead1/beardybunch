from Networking import Server

__author__ = 'Eric'

from time import sleep

pings_recvd = 0

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
        if msg == 'ping':
            #sock.sendall('pong'.encode())
            pings_recvd += 1


if __name__ == '__main__':
    s = ServerTester()
    serv = Server(5555, s)
    serv.start_server()
    while True:
        clients = serv.get_clients()
        i = 0
        for client in clients:
            serv.send_to(client, "Hello from your server, client" + str(i) + "!")
            i += 1
        sleep(0.5)
    serv.stop_server()