import random
import server.db_access as db_access

__author__ = 'Eric'

'''This class represents a game instance. It will handle updating
all the tables in the database for a particular game. Additionally,
it will make decisions such as what cards should be in the case file,
making turns proceed, and handling other game-related activities.'''

class Game:
    def __init__(self):
        _game_id = self.gen_game_id()

    def gen_game_id(self):
        games = db_access.get_games()
        g_id = random.randint
        while id in games:
            g_id = random.randint
        return g_id
