import json

__author__ = 'Eric'

'''Defines message types and provides for the creation and parsing of messages.'''

MESSAGE_TYPES = ['SERVER_PREGAME', 'CLIENT_READY', 'START_GAME', 'MOVE', 'MOVED', 'SUGGEST', 'SUGGESTED',
                 'OFFERREFUTE', 'REFUTE', 'REFUTED', 'DONE', 'GAMEOVER', 'WINNER']

class Message:

    def __init__(self, json_message=None):
        if json_message is None:
            self._message_type = 'NULL'
            self._message_params = {}
        else:
            try:
                msg = json.loads(json_message)
            except ValueError, e:
                print(e)
                raise ValueError
            self._message_type = msg['type']
            self._message_params = msg['params']

    def get_type(self):
        return self._message_type

    def get_params(self):
        return self._message_params

    #Returns true if set to parameter successfully,
    #Returns false if set to NULL.
    def set_type(self, m_type):
        self._message_type = m_type if m_type in MESSAGE_TYPES else 'NULL'
        return False if self._message_type == 'NULL' else True

    def set_params(self, params):
        self._message_params = params

    #flesh out other message types

    '''Creates a message with the given type and parameters.
    m_type should be in MESSAGE_TYPES.
    m_params should be a dictionary of string keys and primitive values
    '''
    def encode_message(self):
        m_type = self._message_type
        return json.dumps({'type': m_type, 'params': self._message_params})