__author__ = 'Eric'

from Networking.Client import Client


if __name__ == '__main__':
    c = Client(('127.0.0.1', 2015))
    inpt = None
    while inpt != 'stop':
        inpt = raw_input("Enter message: ")
        c.send_message(inpt)
        resp = c.get_newest_message()
        print("Response from server: " + repr(resp.decode()))
    c.quit()