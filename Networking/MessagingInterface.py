__author__ = 'Eric'
from abc import ABCMeta, abstractmethod

class MessageListener:
    __metaclass__ = ABCMeta

    @abstractmethod
    def receive_message(self, message):
        pass

    @abstractmethod
    def send_message(self, message):
        pass