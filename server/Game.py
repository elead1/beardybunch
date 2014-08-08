import sys
import random
import threading
import logging
from time import sleep
import server.db_access as db_access
from server.DuplicateTokenError import DuplicateTokenError
from Networking.Server import Server


__author__ = 'Eric'

'''This class represents a game instance. It will handle updating
all the tables in the database for a particular game. Additionally,
it will make decisions such as what cards should be in the case file,
making turns proceed, and handling other game-related activities.'''

_suspect_cards = db_access.get_suspects()
_weapon_cards = db_access.get_weapons()
_location_cards = db_access.get_locations()


class Game():

    def __init__(self):
        self._self_token = self.gen_game_token(self)
        try:
            db_access.insert_new_game(self._self_token)
        except DuplicateTokenError as e:
            print(e.value)
            logging.critical(e.value)
            sys.exit(1)
        self._game_id = self.find_game_id()
        if self._game_id is None:
            print "Failed to create game."
            logging.INFO("Failed to create game. Exiting.")
            sys.exit(1)
        #game_id + 2000 is communication port (to avoid reserved port nums)
        self.server = Server(self._game_id + 2000, self)
        self.server.start_server()
        print "Game created with id {0} and on port {1}".format(self._game_id, self._game_id + 2000)
        logging.info("Game created with id {0} on port {1}".format(self._game_id, self._game_id + 2000))

        logging.info("Starting connection countdown with timer of 45 seconds.")
        timer_thread = threading.Thread(target=self.connect_timer, args=(45, ))
        timer_thread.start()
        timer_thread.join()
        print "timer_thread joined!"

    @staticmethod
    def gen_game_token(self):
        game_tokens = db_access.get_game_tokens()
        g_id = random.randint(0, 0)
        while g_id in game_tokens:
            g_id = random.randint(0, sys.maxsize)  # Note that sys.maxint doesn't represent maxint size in Python3 since integers are automatically converted to longs on overflow.
        return g_id

    def find_game_id(self):
        return db_access.get_game_id_by_token(self._self_token)

    def notify_put(self, q):
        #spawn thread to handle message
        print "stuff 'n' stuff from client"
        pass

    #Thread body to handle client messages; takes decoded message from notify_put and handles it accordingly
    def handle(self, msg):
        #handle various message types
        pass

    #Thread body to handle initial client connections; after 3 connect, waits for 6 to connect or seconds to expire
    def connect_timer(self, seconds):
        num_clients = len(self.server.get_clients())
        expired = False
        while num_clients < 6 and not expired:
            num_clients = len(self.server.get_clients())
            #Don't start counting down until 3 clients connect.
            if num_clients < 3:
                sleep(0.1)
            else:
                seconds -= 1
                if seconds <= 1:
                    expired = True
                sleep(1)
                print seconds


if __name__ == '__main__':
    g = Game()