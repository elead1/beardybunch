#import threading
import logging
import server.db_access as db_access
from server.Game import Game


__author__ = 'Eric'


if __name__ == "__main__":
    logging.basicConfig(filename="ClueServer.log", level=logging.CRITICAL)
    g = Game()
    #print(db_access.get_suspect_id_by_name("Plum"))
    db_access.close_db()