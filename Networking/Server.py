import socket
import Queue
import threading
import hashlib
import logging
from time import sleep

__author__ = 'Eric'
'''Handles connections to clients for a particular game. This includes message passing and waiting for connections for
game start.'''

num_clients = 0


'''Wraps the Queue class with an observer model.'''
class ObservableQueue(Queue.Queue):
    def __init__(self):
        Queue.Queue.__init__(self)
        self.observers = []

    def add_observer(self, obs):
        self.observers.append(obs)

    def remove_observer(self, obs):
        self.observers.remove(obs)

    def put(self, item, block=True, timeout=None):
        Queue.Queue.put(self, item, block, timeout)
        for obs in self.observers:
            obs.notify_put(self)


#Function will be the body of a thread; listens for connections and adds them to list.
#Entries in list are a tuple: (socket connected to client, client address tuple, queue for received data)
def get_connections(control_event, sock, connection_list, list_lock, observer):
    global num_clients
    sock.listen(1)
    while control_event.isSet():
        conn, addr = sock.accept()
        conn.settimeout(0.5)
        obs_q = ObservableQueue()
        obs_q.add_observer(observer)
        #Connection list has socket, name of connection (addr), and an ObservableQueue for handling messages received
        list_lock.acquire()  # Using a lock to ensure the receiver thread's main loop doesn't blow up when the list of clients changes size.
        connection_list[addr] = (conn, addr, obs_q)
        observer.connection_added(addr)
        list_lock.release()
        num_clients += 1
        sleep(0.1)


#Function will be body of a thread; handles receiving messages from clients. If a client is disconnected,
# its socket is cleanly closed.
#Whenever data is received from a client, it is packaged into a dictionary and put into the client's queue.
#Dictionary structure is as follows:
# * 'sender' specifies address of client
# * 'message' specifies the actual data received
def receiver(control_event, connection_list, list_lock):
    global num_clients
    disconnected_clients = []
    while control_event.isSet():
        #Receive from every connected client
        list_lock.acquire()
        for client in connection_list.keys():
            cli = connection_list[client]
            try:
                msg = cli[0].recv(1024)
            #Probably should make this handle things more specifically.
            except socket.timeout as e:
                err = e.args[0]
                if err == 'timed out':
                    continue
                else:
                    print(e)
            except socket.error as e:
                disconnected_clients.append(client)
            else:
                if len(msg) != 0:
                    #Add message sender, message, and involved socket to queue for processing
                    cli[2].put({'sender': cli[1], 'message': msg})
                else:
                    disconnected_clients.append(client)
        #Removes disconnected clients; add logic to redistribute cards/notify client DC'd
        if len(disconnected_clients) != 0:
            for dc in disconnected_clients:
                del connection_list[dc]
                num_clients -= 1
            del disconnected_clients[:]
        list_lock.release()
        sleep(0.1)


class Server:
    def __init__(self, port, queue_observer=None):
        self.connections = {}
        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_sock.bind(('127.0.0.1', port))
        logging.info("Bound server socket on port: " + str(port))
        self.q_observer = queue_observer if queue_observer is not None else self
        self.connection_list_lock = threading.RLock()
        self.server_event = threading.Event()
        self.server_event.set()
        self.receiver_event = threading.Event()
        self.receiver_event.set()
        self.server_thread = threading.Thread(target=get_connections, args=(self.server_event, self.server_sock,
                                                                            self.connections, self.connection_list_lock,
                                                                            self.q_observer))
        self.receiver_thread = threading.Thread(target=receiver, args=(self.receiver_event, self.connections,
                                                                       self.connection_list_lock))

    #Starts the server threads to listen for messages.
    def start_server(self):
        self.server_thread.start()
        logging.info("Started server on port: ", self.server_sock.getsockname())
        self.receiver_thread.start()
        logging.info("Listening for messages.")

    #Shuts down the server threads and terminates connections.
    def stop_server(self):
        self.server_event.clear()
        self.receiver_event.clear()
        self.server_thread.join()
        logging.info("Joined server thread.")
        self.receiver_thread.join()
        logging.info("Joined receiver thread.")
        self.server_sock.close()
        logging.debug("Closed server socket.")
        for addr, client in self.connections.iteritems():
            client[0].close()
            logging.debug("Closed socket for: " + repr(addr))
        logging.info("Closed all sockets.")

    #Callback for the ObservableQueue. Just prints out messages. Instantiating object should override this
    # and register itself as the queue_observer in the init parameters.
    def notify_put(self, q):
        received = q.get()
        sender = received['sender']
        msg = received['message'].decode()
        sock = received['socket']
        print "Received payload from ", repr(sender)
        print "Payload: ", msg

    #Sends payload to designated connected target. Targets are identified by (addr,port) pairs as returned
    # by socket.accept(). Returns the same value as socket.sendall(), or False if it failed to send (client DC).
    def send_to(self, target, payload):
        desig_client = self.connections[target]
        try:
            return desig_client[0].sendall(payload.encode())
        except socket.error, e:
            return False

    #Sends payload to all connected targets. Returns number of targets the payload was sent to.
    def send_to_all(self, payload):
        num_targets_sentto = 0
        for addr, client in self.connections.iteritems():
            try:
                if client[0].sendall(payload.encode()) is None:
                    num_targets_sentto += 1
            except socket.error, e:
                pass
        return num_targets_sentto

    #Returns a list of the connected clients' address tuples
    def get_clients(self):
        clients = self.connections.keys()
        return clients