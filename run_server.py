'''
    Launches a MUD server
'''

import sys
import sqlite3
import threading
from queue import Queue

from server.net_connection import NetConnection
from server.login import Login
from server.play import Play


# Terminal threaded input (so it can other stuff whilst waiting for input)
# Credits: https://stackoverflow.com/a/19655992 (although modified a fair bit now)

def addInput(inputQueue):
    while True:
        inp = input()
        inputQueue.put(inp)

def bindInputToQueue(inputQueue):
    inputThread = threading.Thread(target=addInput, args=(inputQueue,))
    inputThread.daemon = True
    inputThread.start()

if __name__ == '__main__':
    # Handle input in separate thread
    inputQueue = Queue()
    bindInputToQueue(inputQueue)

    # Setup the login state
    login_db = sqlite3.connect(':memory:')
    login_state = Login(login_db)

    # Setup the play state
    play_db = sqlite3.connect(':memory:')
    play_state = Play(play_db)

    # Update in order
    while True:
        try:
            if inputQueue.qsize() > 0:
                commandStr = inputQueue.get()
                if commandStr == "stop":
                    sys.exit()
        except KeyboardInterrupt:
            sys.exit()