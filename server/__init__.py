#import threading
import logging


__author__ = 'Eric'


if __name__ == "__main__":
    logging.basicConfig(filename="E:\Users\Eric\Desktop\GameServer.log", filemode='a',
                            format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                            datefmt='%H:%M:%S',
                            level=logging.INFO)