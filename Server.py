import sys
import socket
import threading

from queue import *

from NetServer import NetServer
from Hook import Hook
from Language import Language
from Dungeon import Dungeon
from Player import Player
from Vector2 import Vector2
from GameState import GameState
from Login import Login

net = None

# Allow for custom ip and port to be defined on startup
if __name__ == "__main__":
    argCount = len(sys.argv)
    ip = argCount > 1 and sys.argv[1] or NetServer.defaultIP
    port = int(argCount > 2 and sys.argv[2] or NetServer.defaultPort)
    net = NetServer(ip, port)
else:
    net = NetServer()

hook = Hook()
dungeon = Dungeon()
login = Login(net, hook)

def handleClientLost(player):
    # Log the player disconnect
    print("Removing lost client: " + player.name)

    # Notify everyone of the disconnect
    net.playersLock.acquire()
    for key in net.players:
        if net.players[key].socket != player.socket:
            string = player.name + " has left the server\n"
            net.Start("Chat")
            net.Write(string)
            net.Send(net.players[key])
    net.playersLock.release()


hook.Add("PlayerLost", "LostMessages", handleClientLost)

def handleClientJoined(player):
    # Update their local game state (defaults to Login in Player)
    net.Start("gamestate")
    net.Write(GameState, GameState.LOGIN)
    net.Send(player)

    # Send login screen
    #login.RequestLogin(player)

    '''
    # Log the player connection
    print("Client joined: " + player.name)

    # Personal Welcome message
    outputToUser = "Welcome to chat, speak your brains here! "
    outputToUser += "You are: " + player.name +"\n"
    outputToUser += "Present in server:\n"

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
    SendRoomInformation(player, dungeon.PositionToRoom(player.pos))
    '''


hook.Add("PlayerJoined", "WelcomeMessages", handleClientJoined)

def main():
    pass
    #net

# Say
def SendLocalChat(turp):
    player, message = turp
    # Only works in play mode
    if player.gameState != GameState.PLAY:
        return

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


hook.Add("PlayerSay", "LocalChat", SendLocalChat)


def HandleSay(netPacket, player):
    message = netPacket.Release()
    hook.Run("PlayerSay", (player, message))


net.Receive("say", HandleSay, lambda player: player.gameState == GameState.PLAY)

# Help
def HandleHelp(netPacket, player):
    net.Start("help")
    net.Write("This is help")
    net.Send(player)

net.Receive("help", HandleHelp, lambda player: player.gameState == GameState.PLAY)

# Go
def HandleGO(netPacket, player):
    netDir = netPacket.Release()

    direction = Language.BaseWordToValue("direction", netDir)

    print(direction)
    print(netDir)

    oldPos = Vector2(player.pos.x, player.pos.y)
    newPos = player.pos + direction

    print("oldPos: " + str(oldPos))
    print("newPos: " + str(newPos))

    print("Valid: " + str(dungeon.IsValidPosition(newPos)))

    if dungeon.IsValidPosition(newPos):
        player.pos = newPos
        room = dungeon.PositionToRoom(player.pos)
        SendRoomInformation(player, room)

        hook.Run("PlayerJoinedRoom", (player, room))
        if oldPos != newPos:
            hook.Run("PlayerLeftRoom", (player, dungeon.PositionToRoom(oldPos)))

    print("Finished GO")

net.Receive("go", HandleGO, lambda player: player.gameState == GameState.PLAY)


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

    print(room.localPos)
    roomPos = dungeon.GlobalPositionFromRoom(room)

    print("Joined: " + str(roomPos))
    print("Running joined room")
    # Other players
    net.playersLock.acquire()

    print("Join room lock acquired")

    # Notify them
    for key in net.players:
        if net.players[key].pos == roomPos and net.players[key] != player:
            net.Start("Chat")
            net.Write(player.nick + " has joined the room!")
            net.Send(net.players[key])

    net.playersLock.release()

    print("Join room lock released")


hook.Add("PlayerJoinedRoom", "ChatMessage", PlayerJoinedRoom)


def PlayerLeftRoom(turp):
    player = turp[0]
    room = turp[1]
    roomPos = dungeon.GlobalPositionFromRoom(room)

    print("Left: " + str(roomPos))

    print("Running left room")
    # Other players
    net.playersLock.acquire()

    print("Leave room lock acquired")

    # Notify them
    for key in net.players:
        if net.players[key].pos == roomPos and net.players[key] != player:
            net.Start("Chat")
            net.Write(player.nick + " has left the room!")
            net.Send(net.players[key])

    net.playersLock.release()

    print("Leave room lock released")

hook.Add("PlayerLeftRoom", "ChatMessage", PlayerLeftRoom)


def ShowPlayers(netPakcet, player):
    playersStr = ""
    playerCount = 0

    net.playersLock.acquire()
    for key in net.players:
        if net.players[key].pos == player.pos and net.players[key] != player:
            playersStr += net.players[key].nick + ", "
            playerCount += 1
    net.playersLock.release()

    if playerCount == 0:
        playersStr = "No players in this room."
    else:
        playersStr = "Players in room: " + playersStr
        playersStr = playersStr[:-2]

    net.Start("Chat")
    net.Write(playersStr)
    net.Send(player)


net.Receive("search", ShowPlayers, lambda player: player.gameState == GameState.PLAY)

while True:
    net.Update()

    #_input = input()
    #if _input == "stop":
        # Save data
        # Close connections (server closing)
    #    print("Stopping server")
    #    net.Stop()
    #    sys.exit()
    #print(_input)
