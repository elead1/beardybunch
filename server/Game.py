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
        #Tracks which suspects were picked by players
        self.assigned_suspects = {}
        #Tracks turns
        self.turn = 0

        self.server = None
        self.casefile = None

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
        else:
            print "Game id is: {0}".format(self._game_id)
            logging.info("Game id: {0}".format(self._game_id))

     #Runs the main body of the Game
    def game_start(self):
        #game_id + 2000 is communication port (to avoid reserved port nums)
        self.server = Server(self._game_id + 2000, self)
        self.server.start_server()
        print "Server created on port {0}".format(self._game_id + 2000)
        logging.info("Server created on port {0}".format(self._game_id + 2000))

        logging.info("Starting connection countdown with timer of {0} seconds.".format(self.countdown_timer))
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
        self.assign_cards(self.casefile)

        db_access.initialize_suspect_locations(self.db[0], self.db[1], self._game_id)

        #Send START_GAME to all clients.
        sus_locs = db_access.get_suspect_locations(self.db[0], self.db[1], self._game_id).values()
        #Logic to pick first player. Necessary if < 6 players.
        self.turn = db_access.get_turn(self.db[0], self.db[1], self._game_id)
        if self.turn not in self.assigned_suspects.keys():
            assigned_susp_keys = self.assigned_suspects.keys()
            assigned_susp_keys.sort()
            self.turn = assigned_susp_keys[0]
            db_access.change_turn(self.db[0], self.db[1], self._game_id, self.turn)
        card_assigns = db_access.get_assigned_cards(self.db[0], self.db[1], self._game_id)
        params = {'suspect_locations': sus_locs, 'suspect_turn': self.turn, 'card_assignments': card_assigns}
        start_game = Game.build_message("START_GAME", params)
        self.server.send_to_all(start_game.encode_message())
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
        suspect = random.choice(_suspect_cards.keys())
        weapon = random.choice(_weapon_cards.keys())
        room = random.choice(_room_cards.keys())
        db_access.assign_card(self.db[0], self.db[1], self._game_id, 'suspect', 0, suspect)
        db_access.assign_card(self.db[0], self.db[1], self._game_id, 'weapon', 0, weapon)
        db_access.assign_card(self.db[0], self.db[1], self._game_id, 'location', 0, room)
        return suspect, weapon, room

    #Assigns cards to players (actually, to their suspect avatars), skipping those in the casefile.
    def assign_cards(self, casefile):
        #Determine who needs cards assigned to them
        self.assigned_suspects = db_access.get_suspect_client_assignments(self.db[0], self.db[1], self._game_id)
        assigned_suspects_ids = self.assigned_suspects.keys()
        #Sort the list so we can deal in turn order
        assigned_suspects_ids.sort()

        #Collect all the cards; reverse keys and values so keys are card names.
        all_cards = {}
        i = 0
        for d in (_suspect_cards, _weapon_cards, _room_cards):
            for k, v in d.iteritems():
                if k != casefile[i]:
                    all_cards[v] = k
            i += 1
        #Get keys (i.e. names) for all cards, so we can determine the proper card type for assignment.
        all_keys = all_cards.keys()

        #Shuffle and assign cards simultaneously
        suspect_iter = 0
        while all_cards:
            choice = random.choice(all_keys)
            #Determine 'type' of card.
            if choice in _suspect_cards.values():
                card_type = 'suspect'
            elif choice in _weapon_cards.values():
                card_type = 'weapon'
            else:
                card_type = 'location'
            card = all_cards.pop(choice)
            db_access.assign_card(self.db[0], self.db[1], self._game_id,
                                  card_type, assigned_suspects_ids[suspect_iter], card)
            all_keys.remove(choice)
            #Assign next card to next suspect
            suspect_iter += 1
            #If we've reached end of suspect list, start over
            if suspect_iter == len(assigned_suspects_ids):
                suspect_iter = 0

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
        self.num_clients = len(self.server.get_clients())
        db = db_access.get_db_access()
        self.client_md5_map[client_id] = hashlib.md5("{0}:{1}".format(client_id[0], client_id[1])).hexdigest()
        avail_susp = db_access.get_unassigned_suspects(db[0], db[1], self._game_id)
        params = {'game_id': self._game_id, 'num_connected': self.num_clients, 'countdown_timer': self.countdown_timer, 'avail_susp': avail_susp.keys()}
        serv_pregame = Game.build_message("SERVER_PREGAME", params)
        self.server.send_to_all(serv_pregame.encode_message())

    #Thread body to handle client messages; takes decoded message from notify_put and handles it according to
    #the specified message type.
    # msg should be a JSON string and should be decoded by Networking.Message.
    def handle(self, sender, msg):
        db = db_access.get_db_access()
        m = Message(msg)
        params = m.get_params()
        if m.get_type() == 'CLIENT_READY':
            client_id = self.client_md5_map[sender]
            db_access.assign_suspect(db[0], db[1], self._game_id, client_id, params['chosen_suspect'])
            avail_susp = db_access.get_unassigned_suspects(db[0], db[1], self._game_id)
            params = {'game_id': self._game_id, 'num_connected': self.num_clients, 'countdown_timer': self.countdown_timer, 'avail_susp': avail_susp.keys()}
            m = Game.build_message("SERVER_PREGAME", params)
            self.server.send_to_all(m.encode_message())
            self.readies_received += 1
        elif m.get_type() == 'MOVE':
            db_access.set_suspect_location(db[0], db[1], self._game_id, params['suspect'], params['new_location'])
            moved_msg = Game.build_message('MOVED', params)
            self.server.send_to_all(moved_msg.encode_message())
        elif m.get_type() == 'DONE':
            print "Received done."
            current_turn = self.turn
            sorted_assigned_suspects = self.assigned_suspects.keys()
            sorted_assigned_suspects.sort()
            #If current turn is the last suspect in turn order, go to first suspect in turn order
            if current_turn == sorted_assigned_suspects[len(sorted_assigned_suspects) - 1]:
                new_turn = sorted_assigned_suspects[0]
            else:
                new_turn = sorted_assigned_suspects[sorted_assigned_suspects.index(current_turn) + 1]
            self.turn = new_turn
            db_access.change_turn(db[0], db[1], self._game_id, self.turn)
            params = {'suspect_turn': self.turn}
            nextturn_msg = Game.build_message('NEXTTURN', params)
            self.server.send_to_all(nextturn_msg.encode_message())
            pass
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
                else:
                    sleep(1)
        self.server.stop_accepting()

    @staticmethod
    def build_message(m_type, param=None):
        m = Message()
        m.set_type(m_type)
        if param:
            m.set_params(param)
        return m

    @staticmethod
    def flip_map(m):
        flipped = {}
        for k, v in m:
            flipped[v] = k
        return flipped

if __name__ == '__main__':
    g = Game(int(sys.argv[1]))
    g.game_start()