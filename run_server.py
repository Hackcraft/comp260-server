'''
    Launches a MUD server
'''

import sys
import sqlite3
import threading
from queue import Queue

from server import *

# Terminal threaded input (so it can other stuff whilst waiting for input)
# Credits: https://stackoverflow.com/a/19655992 (although modified a fair bit now)

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

#
#   Main thread
#
if __name__ == '__main__':
    errorMsg = ""
    players = {}    # connection_id = player
    shouldRun = True

    login_db_file = 'login.sql'
    play_db_file = 'play.sql'

    # Try and connect to a socket
    try:
        net = NetConnection("127.0.0.1", 8222)
    except Exception as e:
        print(e)
        errorMsg += "Unable to bind to ip or port\n"

    # Setup the login state
    try:
        login_db = sqlite3.connect(login_db_file)
        login_state = Login(login_db)
    except Exception as e:
        print(e)
        errorMsg += "Unable to connect to user account (login) database\n"

    # Setup the play state
    try:
        play_db = sqlite3.connect(play_db_file)
        play_state = Play(play_db)
    except Exception as e:
        print(e)
        errorMsg += "Unable to connect to player data database\n"

    # If there's an error - stop server - wait to close TODO Test that it actually works
    if len(errorMsg) > 0:
        shouldRun = False
        print(errorMsg)
        print("Press any key to close.")
        inp = input()
        sys.exit(-1)

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
                print("Found new net connection!")
                index = net.connects.get()
                ply = Player()
                ply.connection_id = index
                players[ply.connection_id] = ply
                login_state.join(ply)

            # Fetch verified logins
            # Send them to the play state
            while login_state.verified_queue.qsize() > 0:
                ply = login_state.verified_queue.get()
                login_state.leave(ply)
                play_state.join(ply)

            # Fetch lost net connections
            # flag and remove them from game states
            while net.disconnects.qsize() > 0:
                connection_id = net.disconnects.get()
                ply = players[connection_id]
                ply.connection_id = None
                login_state.leave(ply)
                play_state.leave(ply)
                players.pop(connection_id, None)
                print("Removed connection id: %s" % connection_id)

            # Update from client messages
            while net.is_pending_recv():
                connection_id, msg = net.recv()

                # If they disconnected - skip pending messages
                if connection_id not in players:
                    continue

                ply = players[connection_id]

                # Not verified - pass messages to Login
                if not ply.login_verified:
                    login_state.update(ply, msg)

                # They are verified - pass messages to Play
                else:
                    play_state.update(ply, msg)

            # Finally send the output from the Login state
            while login_state.output_queue.qsize() > 0:
                ply, msg = login_state.output_queue.get()
                net.send(ply.connection_id, msg)
            # And the Play state
            while play_state.output_queue.qsize() > 0:
                ply, msg = play_state.output_queue.get()
                net.send(ply.connection_id, msg)

        except Exception as e:
            print(e)
        except KeyboardInterrupt:
            sys.exit()