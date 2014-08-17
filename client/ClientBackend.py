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
             'HWAY10': 16, 'CONSERV': 17, 'HWAY11': 18, 'BALL': 19, 'HWAY12': 20, 'KITCHEN': 21}
flipped_locations = flip_map(locations)


class ClientBackend():
    def __init__(self, srv, ui):
        self.ui = ui
        self.serv_addr = srv
        self.comms = Client(srv)
        self.assigned_suspect = None
        self.available_suspects = []
        self.timer_remaining = -1
        self.timer_thread = None

        self.handler_thread = threading.Thread(target=self.handle)
        self.handler_thread.start()

    def suspect_picked_char_select(self, susp_name):
        self.assigned_suspect = susp_name
        client_ready = ClientBackend.build_message("CLIENT_READY", {'chosen_suspect': suspects[susp_name]})
        self.comms.send_message(client_ready.encode_message())

    def handle(self):
        while True:
            msg = self.comms.get_newest_message()
            if msg is None:
                sleep(0.1)
            else:
                m = Message(msg)
                params = m.get_params()
                if m.get_type() == "SERVER_PREGAME":
                    #At least 3 players have joined.
                    print params['num_connected']
                    if params['num_connected'] >= 3:
                        self.timer_remaining = params['countdown_timer']
                        if self.timer_thread is None:
                            self.timer_thread = threading.Thread(target=self.timer_text_updater)
                            self.timer_thread.start()
                    unavail_susp = [x for x in [1, 2, 3, 4, 5, 6] if x not in params['avail_susp']]
                    for card in unavail_susp:
                        susp = flipped_suspects[card]
                        self.ui.gameData['suspects'][susp]['card'].unsetAvailable()
                elif m.get_type() == "START_GAME":
                    self.ui.gameData['currentTurn'] = flipped_suspects[params['suspect_turn']]
                    self.ui.gameData['player']['name'] = self.assigned_suspect
                    assigned_cards = params['card_assignments'][str(suspects[self.assigned_suspect])]
                    for card in assigned_cards:
                        self.ui.gameData['player']['cards']['names'].append(card.upper())
                        self.ui.notes.setChecked(card.upper())
                    if self.ui.gameData['currentTurn'] == self.assigned_suspect:
                        self.ui.gameData['textBox'].setText("YOUR TURN!")
                    else:
                        self.ui.gameData['textBox'].setText("{0}'s turn.".format(self.ui.gameData['currentTurn']))
                    for card in suspects.keys():
                        self.ui.gameData['suspects'][card]['card'].setAvailable()
                        self.ui.gameData['suspects'][card]['room'] = flipped_locations[params['suspect_locations'][suspects[card] - 1]]
                    self.ui.startGame = True

    def timer_text_updater(self):
        while self.timer_remaining > 0:
            old_text = self.ui.gameData['textBox'].getText()
            new_text = "Time remaining before game start: {0}".format(self.timer_remaining)
            self.ui.gameData['textBox'].setText(new_text)
            self.timer_remaining -= 1
            sleep(1)


    @staticmethod
    def build_message(m_type, param):
        m = Message()
        m.set_type(m_type)
        m.set_params(param)
        return m
