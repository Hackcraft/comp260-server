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

    # Try and connect to a socket
    try:
        net = NetConnection("127.0.0.1", 8222)
    except:
        errorMsg += "Unable to bind to ip or port\n"


    # Handle input in separate thread
    inputQueue = Queue()
    bindInputToQueue(inputQueue)

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

    # Errors - TODO stop the server somehow
    if len(errorMsg) > 0:
        print(errorMsg)

    # Update in order
    while True:
        try:
            if inputQueue.qsize() > 0:
                commandStr = inputQueue.get()
                if commandStr == "stop":
                    # TODO any last saves?
                    sys.exit()

            # Move new connections to login
            while net.connects.qsize() > 0:
                index = net.connects.get()
                login_state.join(index)

            # Move logged in to play
            while login_state.verified_queue.qsize() > 0:
                index = login_state.verified_queue.get()
                player_id = None # TODO LOAD player data such as room from username?
                ply = Player(index, play_state) # TODO Should the player object know about the gameState classes?

            # Check for disconnections


            # Update from client messages
            while net.is_pending_recv():
                client, msg = net.recv()



        except KeyboardInterrupt:
            sys.exit()