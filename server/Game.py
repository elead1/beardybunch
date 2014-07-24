import os
import sys
import random
import logging
import Networking.MessagingInterface as MessagingInterface
import server.db_access as db_access
from server.DuplicateTokenError import DuplicateTokenError
from server.Server import ConnectionManager
from time import sleep

__author__ = 'Eric'

'''This class represents a game instance. It will handle updating
all the tables in the database for a particular game. Additionally,
it will make decisions such as what cards should be in the case file,
making turns proceed, and handling other game-related activities.'''

_suspect_cards = db_access.get_suspects()
_weapon_cards = db_access.get_weapons()
_location_cards = db_access.get_locations()

class Game(MessagingInterface):

    def __init__(self):
        self._self_token = self.gen_game_token()
        try:
            db_access.insert_new_game(self._self_token)
        except DuplicateTokenError as e:
            print(e.value)
            logging.critical(e.value)
            sys.exit(1)
        self._game_id = self.find_game_id()
        if self._game_id is None:
            print("Failed to create game.")
            logging.INFO("Failed to create game. Exiting.")
            sys.exit(1)
        #game_id is communication port
        self.server = ConnectionManager(self.game_id)

        print("Game created with id: ", self._game_id)
        logging.info("Game created with id: ", self._game_id)

        while not self.server.should_start_game():
            #Wait for game to be okay to start.
            sleep(1)


    @staticmethod
    def gen_game_token(self):
        game_tokens = db_access.get_game_tokens()
        g_id = random.randint(0, 0)
        while g_id in game_tokens:
            g_id = random.randint(0, sys.maxsize)  # Note that sys.maxint doesn't represent maxint size in Python3 since integers are automatically converted to longs on overflow.
        return g_id

    def find_game_id(self):
        return db_access.get_game_id_by_token(self._self_token)