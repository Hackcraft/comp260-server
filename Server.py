import sys
import socket
import threading

from queue import *

from NetServer import NetServer
#from Commands import *
from Dungeon import Dungeon
from Player import Player

net = NetServer()

messageQueue = Queue()

clientIndex = 0
currentClients = {}
currentClientsLock = threading.Lock()

def handleClientLost(command):
    currentClientsLock.acquire()
    lostClient = currentClients[command.socket]
    print("Removing lost client: client-"+str(lostClient))

    for clientSocket in currentClients:
        if clientSocket != command.socket:
            string = "client-" + lostClient.GetName() + " has left the chat room\n"
            net.Start("Chat")
            net.Write(outputToUser)
            net.Send(clientSocket)

    del currentClients[command.socket]

    currentClientsLock.release()

def handleClientJoined(command):
    global clientIndex

    currentClientsLock.acquire()
    currentClients[command.socket] = Player(command.socket, "Client " + str(clientIndex))
    clientIndex += 1

    # Log the player connection
    print("Client joined: client-" + currentClients[command.socket].GetName())

    # Personal Welcome message
    outputToUser = "Welcome to chat, speak your brains here! "
    outputToUser += "Currently all you can do is type to others and use the 'go' command followed by the direction (north/east/south/west)\n"
    outputToUser += "You are: client-" + currentClients[command.socket].GetName() +"\n"
    outputToUser += "Present in chat:\n"

    # Personal list of connected clients
    for key in currentClients:
        outputToUser += "client-" + currentClients[key].GetName() + "\n"

    net.Start("Chat")
    net.Write(outputToUser)
    net.Send(command.socket)

    # Notify everyone of the new arrival
    for clientSocket in currentClients:
        if clientSocket != command.socket:
            string = "client-" + currentClients[command.socket].GetName() + " has joined the chat room\n"
            net.Start("Chat")
            net.Write(outputToUser)
            net.Send(clientSocket)

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

# Say
def HandleSay(netPacket, clientSocket):
    pass

net.Receive("say", HandleSay)

# Go
def HandleGO(netPacket, clientSocket):
    pass

net.Receive("go", HandleGO)

# Help
def HandleHelp(netPacket, clientSocket):
    pass

net.Receive("help", HandleGO)


if __name__ == "__main__":
    main()