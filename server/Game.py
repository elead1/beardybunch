import sys
import random
import threading
import logging
import hashlib
from time import sleep
import server.db_access as db_access
from server.DuplicateTokenError import DuplicateTokenError
from Networking.Server import Server
from Networking.Message import Message


__author__ = 'Eric'

'''This class represents a game instance. It will handle updating
all the tables in the database for a particular game. Additionally,
it will make decisions such as what cards should be in the case file,
making turns proceed, and handling other game-related activities.'''

init_access = db_access.get_db_access()
_suspect_cards = db_access.get_suspects(init_access[0], init_access[1])
_weapon_cards = db_access.get_weapons(init_access[0], init_access[1])
_location_cards = db_access.get_locations(init_access[0], init_access[1])
_room_cards = db_access.get_rooms(init_access[0], init_access[1])
db_access.close_db(init_access[0], init_access[1])


#start_timeout: the time to wait for clients to connect
class Game():

    def __init__(self, start_timeout):
        #Get connection, cursor tuple for DB access
        self.db = db_access.get_db_access()
        self._self_token = self.gen_game_token(self)
        self.countdown_timer = start_timeout
        #Number of connected clients; tracked for convenience
        self.num_clients = 0
        #Number of readies received; tracked for convenience
        self.readies_received = 0
        #Map of (ip, port) client identifying tuples to md5 hashes of ip:port strings (hash used as client id in DB)
        self.client_md5_map = {}

        try:
            db_access.insert_new_game(self.db[0], self.db[1], self._self_token)
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
        timer_thread = threading.Thread(target=self.connect_timer)
        timer_thread.start()
        timer_thread.join()
        while self.readies_received != self.num_clients:
            sleep(0.1)
        logging.info("Finished waiting for clients. Number of clients connected: {0}".format(self.num_clients))
        logging.info("Client identifiers: {0}".format(self.client_md5_map.keys()))
        assigns = db_access.get_suspect_client_assignments(self.db[0], self.db[1], self._game_id)
        logging.info("Client avatar assignments: {0}".format(repr(assigns)))

        #Select case file and assign cards to players.
        self.casefile = self.generate_casefile()
        #self.assign_cards(self.casefile)

        #db_access.initialize_suspect_locations(self.db[0], self.db[1], self._game_id)

        #Send START_GAME to all clients.
        sys.exit(0)
        pass

    @staticmethod
    def gen_game_token(self):
        game_tokens = db_access.get_game_tokens(self.db[0], self.db[1])
        g_id = random.randint(0, 0)
        while g_id in game_tokens:
            g_id = random.randint(0, sys.maxsize)  # Note that sys.maxint doesn't represent maxint size in Python3 since integers are automatically converted to longs on overflow.
        return g_id

    def find_game_id(self):
        return db_access.get_game_id_by_token(self.db[0], self.db[1], self._self_token)

    #Chooses which card from each category will make up the case file for this game.
    def generate_casefile(self):
        suspect = random.randint(1, len(_suspect_cards.keys()))
        weapon = random.randint(1, len(_weapon_cards.keys()))
        room = random.randint(1, len(_room_cards.keys()))
        db_access.assign_card(self.db[0], self.db[1], self._game_id, 'suspect', 0, suspect)
        db_access.assign_card(self.db[0], self.db[1], self._game_id, 'weapon', 0, weapon)
        db_access.assign_card(self.db[0], self.db[1], self._game_id, 'location', 0, room)
        return suspect, weapon, room

    #Assigns cards to players (actually, to their suspect avatars), skipping those in the casefile.
    def assign_cards(self, casefile):
        #assigned_suspects = db_access.get_suspect_client_assignments(self.db[0], self.db[1], self._game_id)
        pass

    #q is a Queue that received an entry.
    #q.get() returns that entry.
    #In this case, each Queue entry is a dictionary like this:
    # * 'sender' specifies address of client
    # * 'message' specifies the actual data received; encoded using Python's .encode()
    def notify_put(self, q):
        #spawn thread to handle message
        payload = q.get()
        handle_thread = threading.Thread(target=self.handle, args=(payload['sender'], payload['message'].decode(),))
        handle_thread.start()
        handle_thread.join()

    #Called when a new connection is made to the server.
    def connection_added(self, client_id):
        db = db_access.get_db_access()
        self.client_md5_map[client_id] = hashlib.md5("{0}:{1}".format(client_id[0], client_id[1])).hexdigest()
        avail_susp = db_access.get_unassigned_suspects(db[0], db[1], self._game_id)
        params = {'game_id': self._game_id, 'countdown_timer': self.countdown_timer, 'avail_susp': avail_susp.keys()}
        serv_pregame = self.build_message("SERVER_PREGAME", params)
        self.server.send_to_all(serv_pregame.encode_message())

    #Thread body to handle client messages; takes decoded message from notify_put and handles it according to
    #the specified message type.
    # msg should be a JSON string and should be decoded by Networking.Message.
    def handle(self, sender, msg):
        db = db_access.get_db_access()
        m = Message(msg)
        if m.get_type() == 'CLIENT_READY':
            client_id = self.client_md5_map[sender]
            params = m.get_params()
            db_access.assign_suspect(db[0], db[1], self._game_id, client_id, params['chosen_suspect'])
            avail_susp = db_access.get_unassigned_suspects(db[0], db[1], self._game_id)
            params = {'game_id': self._game_id, 'countdown_timer': self.countdown_timer, 'avail_susp': avail_susp.keys()}
            m = self.build_message("SERVER_PREGAME", params)
            self.server.send_to_all(m.encode_message())
            self.readies_received += 1
        db_access.close_db(db[0], db[1])

    #Thread body to handle initial client connections; after 3 connect, waits for 6 to connect or seconds to expire
    def connect_timer(self):
        self.num_clients = len(self.server.get_clients())
        expired = False
        while self.num_clients < 6 and not expired:
            self.num_clients = len(self.server.get_clients())
            #Don't start counting down until 3 clients connect.
            if self.num_clients < 3:
                sleep(0.1)
            else:
                self.countdown_timer -= 1
                if self.countdown_timer < 1:
                    expired = True
                sleep(1)

    @staticmethod
    def build_message(m_type, param):
        m = Message()
        m.set_type(m_type)
        m.set_params(param)
        return m


if __name__ == '__main__':
    g = Game(5)