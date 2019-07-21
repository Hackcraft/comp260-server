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
from server.net_connection import NetConnection
from server.player import Player

# Terminal threaded input (so it can other stuff whilst waiting for input)
# Credits: https://stackoverflow.com/a/19655992 (although modified a fair bit now)

#
#   Convert from temporary connection indexes to persistent player ids and back
#
class IdToIndexLinker:

    def __init__(self):
        self.id_to_index = {}
        self.index_to_id = {}

    def id_from_index(self, index):
        return self.index_to_id.get(index, None)

    def index_from_id(self, id):
        return self.id_to_index.get(id, None)

    def index_has_id(self, index):
        return self.id_from_index(index) is not None

    def id_has_index(self, id):
        return self.index_from_id(id) is not None

    def link_id_to_index(self, id, index):
        self.link_index_to_id(index, id)

    def link_index_to_id(self, index, id):
        self.id_to_index[id] = index
        self.index_to_id[index] = id

    def remove_link(self, index = None, id = None):
        if index is not None:
            id = self.id_from_index(index)
            self.id_to_index.pop(id, None)
            self.index_to_id.pop(index, None)
        elif id is not None:
            index = self.index_from_id(id)
            self.id_to_index.pop(id, None)
            self.index_to_id.pop(index, None)

#
#   Console input handling
#
def addInput(inputQueue):
    while True:
        inp = input()
        inputQueue.put(inp)

def bindInputToQueue(inputQueue):
    inputThread = threading.Thread(target=addInput, args=(inputQueue,))
    inputThread.daemon = True
    inputThread.start()

if __name__ == '__main__':
    errorMsg = ""
    players = {}
    shouldRun = True

    id_linker = IdToIndexLinker()

    # Try and connect to a socket
    try:
        net = NetConnection("127.0.0.1", 8222)
    except:
        errorMsg += "Unable to bind to ip or port\n"

    # Setup the login state
    try:
        login_db = sqlite3.connect(':memory:')
        login_state = Login(login_db)
    except:
        errorMsg += "Unable to connect to user account (login) database\n"

    # Setup the play state
    try:
        play_db = sqlite3.connect(':memory:')
        play_state = Play(play_db)
    except:
        errorMsg += "Unable to connect to player data database\n"

    # If there's an error - stop server - wait to close TODO Test that it actually works
    if len(errorMsg) > 0:
        print(errorMsg)
        print("Press any key to close.")
        inp = input()
        sys.exit(-1)
        shouldRun = False

    # Handle input in separate thread
    inputQueue = Queue()
    bindInputToQueue(inputQueue)

    # Update in order
    while shouldRun:
        try:
            # Wait for stop command
            if inputQueue.qsize() > 0:
                commandStr = inputQueue.get()
                if commandStr == "stop":
                    # TODO any last saves?
                    sys.exit()

            # Fetch new net connections
            # Send them to the login state
            while net.connects.qsize() > 0:
                index = net.connects.get()
                ply = Player()
                ply.connection_id = index
                login_state.join(ply)

            # Fetch verified logins
            # Send them to the play state
            while login_state.verified_queue.qsize() > 0:
                ply = login_state.verified_queue.get()
                login_state.leave(ply)
                play_state.join(ply)

            # Check for disconnections


            # Update from client messages
            while net.is_pending_recv():
                client, msg = net.recv()



        except KeyboardInterrupt:
            sys.exit()