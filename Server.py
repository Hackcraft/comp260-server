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
dungeon = Dungeon()

def handleClientLost(player):
    # Log the player disconnect
    print("Removing lost client: " + player.name)

    # Notify everyone of the disconnect
    net.playersLock.acquire()
    for key in net.players:
        if net.players[key].socket != player.socket:
            string = player.name + " has left the chat room\n"
            net.Start("Chat")
            net.Write(string)
            net.Send(net.players[key])
    net.playersLock.release()


hook.Add("PlayerLost", "LostMessages", handleClientLost)

def handleClientJoined(player):
    # Log the player connection
    print("Client joined: " + player.name)

    # Personal Welcome message
    outputToUser = "Welcome to chat, speak your brains here! "
    outputToUser += "Currently all you can do is type to others and use the 'go' command followed by the direction (north/east/south/west)\n"
    outputToUser += "You are: " + player.name +"\n"
    outputToUser += "Present in chat:\n"

    # Personal list of connected clients
    net.playersLock.acquire()
    for key in net.players:
        if net.players[key] != player:
            outputToUser += net.players[key].name + "\n"
    net.playersLock.release()

    net.Start("Chat")
    net.Write(outputToUser)
    net.Send(player)

    # Notify everyone of the new arrival
    net.playersLock.acquire()
    for key in net.players:
        if net.players[key].socket != player.socket:
            string = player.name + " has joined the chat room\n"
            net.Start("Chat")
            net.Write(string)
            net.Send(net.players[key])
    net.playersLock.release()

    # Room information
    print("infos")
    SendRoomInformation(player, dungeon.PositionToRoom(player.pos))


hook.Add("PlayerJoined", "WelcomeMessages", handleClientJoined)

def main():
    pass
    #net

# Say
def HandleSay(netPacket, player):
    message = netPacket.Release()

    # Other players
    net.playersLock.acquire()
    players = net.players
    net.playersLock.release()

    # Notify them
    for key in players:
        if players[key].pos == player.pos:
            net.Start("Chat")
            net.Write(player.name + ": " + message)
            net.Send(players[key])

net.Receive("say", HandleSay)

# Help
def HandleHelp(netPacket, player):
    net.Start("help")
    net.Write("This is help")
    net.Send(player)

net.Receive("help", HandleHelp)

# Go
def HandleGO(netPacket, player):
    netDir = netPacket.Release()
    direction = Language.BaseWordToValue("direction", netDir)

    print(direction)
    print(netDir)

    oldPos = player.pos
    newPos = player.pos + direction

    print("oldPos: " + str(oldPos))
    print("newPos: " + str(newPos))

    print("Valid: " + str(dungeon.IsValidPosition(newPos)))

    if dungeon.IsValidPosition(newPos):
        player.pos = newPos
        room = dungeon.PositionToRoom(player.pos)
        SendRoomInformation(player, room)

        hook.Run("PlayerJoinedRoom", (player, room))
        hook.Run("PlayerLeftRoom", (player, dungeon.PositionToRoom(oldPos)))

    print("Finished GO")

net.Receive("go", HandleGO)


def SendRoomInformation(player, room):
    print("SendRoomInformation")
    # Moving player
    roomStr = ""
    for x in range(0, len(room.connections)):
        roomStr += str(room.connections[x]) + ","
    roomStr = roomStr[:-1] #  Remove the last comma

    net.Start("EnteredRoom")
    net.Write(roomStr)  # connections
    net.Write(room.description)  # description
    net.Send(player)


def PlayerJoinedRoom(turp):
    player = turp[0]
    room = turp[1]
    print("Running joined room")
    # Other players
    net.playersLock.acquire()

    print("Join room lock acquired")

    # Notify them
    for key in net.players:
        if net.players[key].pos == player.pos and net.players[key] != player:
            net.Start("Chat")
            net.Write(player.name + " has joined the room!")
            net.Send(net.players[key])

    net.playersLock.release()

    print("Join room lock released")


hook.Add("PlayerJoinedRoom", "ChatMessage", PlayerJoinedRoom)


def PlayerLeftRoom(turp):
    player = turp[0]
    room = turp[1]
    roomPos = dungeon.GlobalPositionFromRoom(room)

    print("Running left room")
    # Other players
    net.playersLock.acquire()

    print("Leave room lock acquired")

    # Notify them
    for key in net.players:
        if net.players[key].pos != roomPos and net.players[key] != player:
            net.Start("Chat")
            net.Write(player.name + " has left the room!")
            net.Send(net.players[key])

    net.playersLock.release()

    print("Leave room lock released")

hook.Add("PlayerLeftRoom", "ChatMessage", PlayerLeftRoom)


if __name__ == "__main__":
    main()