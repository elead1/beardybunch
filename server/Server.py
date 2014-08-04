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


'''Handles different message types'''
class ServerQueueObserver():
    def __init__(self):
        pass

    def notify_put(self, q):
        pass


'''Wraps the Queue class with an observer model.'''
class ObservableQueue(Queue.Queue):
    def __init__(self):
        super(Queue.Queue, self).__init__()
        self.observers = []

    def add_observer(self, obs):
        self.observers.append(obs)

    def remove_observer(self, obs):
        self.observers.remove(obs)

    def put(self, item, block=True, timeout=None):
        super(Queue.Queue, self).put(item, block, timeout)
        for obs in self.observers:
            obs.notify_put(self)


'''Function will be the body of a thread; listens for connections and adds them to list.
TODO: Add logic to restrict to 6 connections/start countdown timer.'''
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
        connection_list.append((conn, addr, obs_q))
        list_lock.release()
        num_clients += 1
        sleep(0.1)


'''Function will be body of a thread; handles receiving messages from clients.'''
def receiver(control_event, connection_list, list_lock):
    global num_clients
    disconnected_clients = []
    while control_event.isSet():
        #Receive from every connected client
        list_lock.acquire()
        for client in connection_list:
            try:
                msg = client[0].recv(1024)
            #Probably should make this handle things more specifically.
            except socket.timeout as e:
                err = e.args[0]
                if err == 'timed out':
                    continue
                else:
                    print(e)
            except socket.error as e:
                print(e)
            else:
                if len(msg) != 0:
                    #Add message sender, message, and involved socket to queue for processing
                    client[2].put({'sender': client[1], 'message': msg, 'socket': client[0]})
                else:
                    disconnected_clients.append(client)
        #Removes disconnected clients; add logic to redistribute cards
        if len(disconnected_clients) != 0:
            for dc in disconnected_clients:
                connection_list.remove(dc)
                num_clients -= 1
            disconnected_clients.clear()
        list_lock.release()
        sleep(0.1)


class Server:
    def __init__(self, port):
        self.connections = []
        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_sock.bind(('127.0.0.1', port))
        self.connection_list_lock = threading.RLock()
        self.server_event = threading.Event()
        self.server_event.set()
        self.receiver_event = threading.Event()
        self.receiver_event.set()
        self.q_obs = ServerQueueObserver()
        self.server_thread = threading.Thread(target=get_connections, args=(self.server_event, self.server_sock,
                                                                            self.connections, self.connection_list_lock,
                                                                            self.q_obs))
        self.receiver_thread = threading.Thread(target=receiver, args=(self.receiver_event, self.connections,
                                                                       self.connection_list_lock))

    def start_server(self):
        self.server_thread.start()
        logging.info("Started server on port: ", self.server_sock.getsockname())
        self.receiver_thread.start()
        logging.info("Listening for messages.")

    def stop_server(self):
        self.server_event.clear()
        self.receiver_event.clear()
        self.server_thread.join()
        self.receiver_thread.join()