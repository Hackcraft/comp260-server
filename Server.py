import sys
import socket
import threading

from queue import *

from NetServer import NetServer
from Hook import Hook
from Language import Language
#from Commands import *
from Dungeon import Dungeon
from Player import Player

net = NetServer()
hook = Hook()

messageQueue = Queue()

clientIndex = 0
currentClients = {}
currentClientsLock = threading.Lock()

def handleClientLost(player):
    # Log the player disconnect
    print("Removing lost client: client-" + player.name)

    # Notify everyone of the disconnect
    net.playersLock.acquire()
    for ply in net.players:
        if ply.socket != player.socket:
            string = "client-" + player.name + " has left the chat room\n"
            net.Start("Chat")
            net.Write(string)
            net.Send(ply.socket)
    net.playersLock.release()


hook.Add("PlayerLost", "LostMessages", handleClientLost)

def handleClientJoined(player):
    # Log the player connection
    print("Client joined: client-" + player.name)

    # Personal Welcome message
    outputToUser = "Welcome to chat, speak your brains here! "
    outputToUser += "Currently all you can do is type to others and use the 'go' command followed by the direction (north/east/south/west)\n"
    outputToUser += "You are: client-" + player.name +"\n"
    outputToUser += "Present in chat:\n"

    # Personal list of connected clients
    net.playersLock.acquire()
    for key in net.players:
        outputToUser += "client-" + net.players[key].name + "\n"
    net.playersLock.release()

    net.Start("Chat")
    net.Write(outputToUser)
    net.Send(player.socket)

    # Notify everyone of the new arrival
    net.playersLock.acquire()
    for key in net.players:
        if net.players[key].socket != player.socket:
            string = "client-" + player.name + " has joined the chat room\n"
            net.Start("Chat")
            net.Write(string)
            net.Send(net.players[key].socket)
    net.playersLock.release()


hook.Add("PlayerJoined", "WelcomeMessages", handleClientJoined)

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
def HandleGO(netPacket, player):
    direction = Language.BaseWordToValue(netPacket.Release())

    newPos = player

net.Receive("go", HandleGO)

# Help
def HandleHelp(netPacket, player):
    net.Start("help")
    net.Write("This is help")
    net.Send(player)

net.Receive("help", HandleHelp)


if __name__ == "__main__":
    main()