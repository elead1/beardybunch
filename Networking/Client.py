import socket
import sys
import Queue
import threading
import hashlib
import logging
from time import sleep

__author__ = 'Eric'


#Listens to the socket for data and adds it to the queue of messages.
def listen_for_messages(sock, control_event, msg_q):
    while not control_event.is_set():
        try:
            msg = sock.recv(1024)
        #Probably should make this handle things more specifically.
        except socket.timeout as e:
            err = e.args[0]
            if err == 'timed out':
                continue
            else:
                logging.error(e)
        except socket.error as e:
            logging.critical("Disconnected from server! So sad :-(")
            sys.exit(-1)
        else:
            if len(msg) != 0:
                #Add still-encoded message to queue for processing
                msg_q.put(msg)
            else:
                logging.critical("Disconnected from server! So sad :-(")
                sys.exit(-1)

class Client:
    def __init__(self, server_addr):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.receive_queue = Queue.Queue()
        self.control = threading.Event()
        self.control.clear()
        logging.info("Connecting to server at {0}:{1}".format(server_addr[0], server_addr[1]))
        try:
            self.sock.connect(server_addr)
        except socket.error, e:
            logging.critical("Could not connect to server.")
            logging.critical(e)
            sys.exit(0)
        self.listen_thread = threading.Thread(target=listen_for_messages,
                                              args=(self.sock, self.control, self.receive_queue))
        self.listen_thread.start()

    def get_newest_message(self):
        return self.receive_queue.get()

    def send_message(self, message):
        return self.sock.sendall(message.encode())

    def quit(self):
        self.control.set()
        logging.info("Client joining listener thread.")
        self.listen_thread.join()
        self.sock.close()
