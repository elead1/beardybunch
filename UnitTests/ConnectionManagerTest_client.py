__author__ = 'Eric'
from time import sleep
from Networking.Client import Client
from Networking.Message import Message


if __name__ == '__main__':
    c = Client(('127.0.0.1', 2003))
    inpt = None
    resp = c.get_newest_message()
    print("Response from server: " + repr(resp.decode()))
    ready = Message()
    ready.set_type('CLIENT_READY')
    ready.set_params({'chosen_suspect': 6})
    c.send_message(ready.encode_message())
    while inpt != 'stop':
        resp = c.get_newest_message()
        print "Message from server: " + repr(resp.decode())
        sleep(0.25)
    c.quit()