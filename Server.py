import sys
import socket
import threading

from queue import *

from NetServer import NetServer
from Commands import *
from Dungeon import Dungeon

net = NetServer()

messageQueue = Queue()

clientIndex = 0
currentClients = {}
currentClientsLock = threading.Lock()

def handleClientLost(command):
    currentClientsLock.acquire()
    lostClient = currentClients[command.socket]
    print("Removing lost client: client-"+str(lostClient))

    for key in currentClients:
        if key != command.socket:
            key.send(bytes("client-"+str(lostClient) + " has left the chat room", 'utf-8'))

    del currentClients[command.socket]

    currentClientsLock.release()

def handleClientJoined(command):
    global clientIndex

    currentClientsLock.acquire()
    currentClients[command.socket] = clientIndex
    clientIndex += 1

    print("Client joined: client-" + str(currentClients[command.socket]))

    outputToUser = "Welcome to chat, speak your brains here! "
    outputToUser += "Currently all you can do is type to others and use the 'go' command followed by the direction (north/east/south/west)\n"
    outputToUser += "You are: client-" + str(currentClients[command.socket]) +"\n"
    outputToUser += "Present in chat:\n"


    for key in currentClients:
        outputToUser += "client-" + str(currentClients[key]) + "\n"

    command.socket.send(bytes(outputToUser, 'utf-8') )

    for key in currentClients:
        if key != command.socket:
            key.send(bytes("client-"+str(currentClients[command.socket]) + " has joined the chat room", 'utf-8'))

    # Tell them who they are
    command.socket.send(("you- " + str(currentClients[command.socket])).encode())
    # Tell them which room to start in
    command.socket.send(("move- " + str(currentClients[command.socket]) + " 0" ).encode())

    currentClientsLock.release()

def handleClientMessage(command):
    print("client message: "+command.message)

    currentClientsLock.acquire()
    for key in currentClients:
        try:
            key.send(bytes(command.message,'utf-8'))
        except socket.error:
            messageQueue.put(ClientLost(key))

    currentClientsLock.release()

def main():
    pass
    #net


if __name__ == "__main__":
    main()