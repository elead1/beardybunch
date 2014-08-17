__author__ = 'Eric'

from time import sleep
import threading
from Networking.Client import Client
from Networking.Message import Message


def flip_map(m):
    flipped = {}
    for k, v in m.iteritems():
        flipped[v] = k
    return flipped


suspects = {'SCARLET': 1, 'MUSTARD': 2, 'WHITE': 3, 'GREEN': 4, 'PEACOCK': 5, 'PLUM': 6}
flipped_suspects = flip_map(suspects)
locations = {'STUDY': 1, 'HWAY1': 2, 'HALL': 3, 'HWAY2': 4, 'LOUNGE': 5, 'HWAY3': 6, 'HWAY4': 7, 'HWAY5': 8,
             'LIBRARY': 9, 'HWAY6': 10, 'BILLIARD': 11, 'HWAY7': 12, 'DINING': 13, 'HWAY8': 14, 'HWAY9': 15,
             'HWAY10': 16, 'CONSERVATORY': 17, 'HWAY11': 18, 'BALLROOM': 19, 'HWAY12': 20, 'KITCHEN': 21}
flipped_locations = flip_map(locations)
valid_moves = {1: [2, 6, 21], 2: [1, 3], 3: [2, 4, 7], 4: [3, 5], 5: [4, 8, 17], 6: [1, 9], 7: [3, 11], 8: [5, 13],
               9: [6, 10, 14], 10: [9, 11], 11: [10, 7, 12, 15], 12: [11, 13], 13: [12, 8, 16], 14: [9, 17],
               15: [11, 19], 16: [13, 21], 17: [14, 18, 5], 18: [17, 19], 19: [18, 15, 20], 20: [19, 21],
               21: [20, 16, 1]}

class ClientBackend():
    def __init__(self, srv, ui):
        self.ui = ui
        self.serv_addr = srv
        self.comms = Client(srv)
        self.assigned_suspect = None
        self.available_suspects = []
        self.my_loc = None
        self.timer_remaining = -1
        self.timer_thread = None


        self.handler_thread = threading.Thread(target=self.handle)
        self.handler_thread.start()

        self.main_thread = threading.Thread(target=self.run_game)
        self.main_thread.start()

    def suspect_picked_char_select(self, susp_name):
        self.assigned_suspect = susp_name
        client_ready = ClientBackend.build_message("CLIENT_READY", {'chosen_suspect': suspects[susp_name]})
        self.comms.send_message(client_ready.encode_message())

    def player_moved_ok(self, new_room):
        old_room = self.my_loc
        if locations[new_room] in valid_moves[locations[old_room]]:
            self.ui.gameData['lastPlayMode'] = 'TURN'
            self.my_loc = new_room
            params = {'suspect': suspects[self.assigned_suspect], 'new_location': locations[self.my_loc]}
            moved_msg = ClientBackend.build_message('MOVE', params)
            self.comms.send_message(moved_msg.encode_message())
            return True
        else:
            self.ui.gameData['textBox'].setText("Invalid move.")
            return False

    def turn_done(self):
        done_msg = ClientBackend.build_message('DONE')
        self.comms.send_message(done_msg.encode_message())

    def run_game(self):
        while True:
            if self.ui.gameData['mode'] == 'PLAY':
                if self.ui.gameData['currentTurn'] == self.assigned_suspect and self.ui.gameData['lastPlayMode'] != 'TURN':
                    self.ui.gameData['playMode'] = 'TURN'
                if self.ui.gameData['playMode'] == 'WAIT':
                    pass
                if self.ui.gameData['playMode'] == 'TURN':
                    pass
            elif self.ui.gameData['mode'] == 'CHOOSECHAR':
                pass
            sleep(0.1)

    def handle(self):
        while True:
            msg = self.comms.get_newest_message()
            if msg is None:
                sleep(0.1)
            else:
                m = Message(msg)
                params = m.get_params()
                #SERVER PREGAME
                if m.get_type() == "SERVER_PREGAME":
                    #At least 3 players have joined.
                    if params['num_connected'] >= 3:
                        self.timer_remaining = params['countdown_timer']
                        if self.timer_thread is None:
                            self.timer_thread = threading.Thread(target=self.timer_text_updater)
                            self.timer_thread.start()
                    unavail_susp = [x for x in [1, 2, 3, 4, 5, 6] if x not in params['avail_susp']]
                    for card in unavail_susp:
                        susp = flipped_suspects[card]
                        self.ui.gameData['suspects'][susp]['card'].unsetAvailable()
                #START GAME
                elif m.get_type() == "START_GAME":
                    self.ui.gameData['currentTurn'] = flipped_suspects[params['suspect_turn']]
                    self.ui.gameData['player']['name'] = self.assigned_suspect
                    #Grab this player's assigned cards.
                    assigned_cards = params['card_assignments'][str(suspects[self.assigned_suspect])]
                    #Check 'em off in Notes
                    for card in assigned_cards:
                        self.ui.gameData['player']['cards']['names'].append(card.upper())
                        self.ui.notes.setChecked(card.upper())
                    #Add entry in log for whose turn it is
                    self.note_turn_change()
                    #Move suspects to proper locations.
                    for card in suspects.keys():
                        self.ui.gameData['suspects'][card]['card'].setAvailable()
                        self.ui.gameData['suspects'][card]['room'] = flipped_locations[params['suspect_locations'][suspects[card] - 1]]
                    self.my_loc = self.ui.gameData['suspects'][self.assigned_suspect]['room']
                    self.ui.startGame = True
                elif m.get_type() == "MOVED":
                    self.ui.gameData['suspects'][flipped_suspects[params['suspect']]]['room'] = flipped_locations[params['new_location']]
                elif m.get_type() == "NEXTTURN":
                    self.ui.gameData['currentTurn'] = flipped_suspects[params['suspect_turn']]
                    self.note_turn_change()
                else:
                    print "Received unknown message type: {0}".format(m.get_type())

    def timer_text_updater(self):
        while self.timer_remaining > 0:
            old_text = self.ui.gameData['textBox'].getText()
            new_text = "Time remaining before game start: {0}".format(self.timer_remaining)
            self.ui.gameData['textBox'].setText(new_text)
            self.timer_remaining -= 1
            sleep(1)

    def note_turn_change(self):
        if self.ui.gameData['currentTurn'] == self.assigned_suspect:
            self.ui.gameData['textBox'].setText("YOUR TURN!")
        else:
            self.ui.gameData['textBox'].setText("{0}'s turn.".format(self.ui.gameData['currentTurn']))

    @staticmethod
    def build_message(m_type, param=None):
        m = Message()
        m.set_type(m_type)
        if param:
            m.set_params(param)
        return m
