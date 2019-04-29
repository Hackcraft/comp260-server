import sys
import PyQt5.QtCore
import PyQt5.QtWidgets

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import QtCore
from Dungeon import Dungeon
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QGuiApplication
from PyQt5.QtQml import QQmlApplicationEngine


import socket
import threading
from queue import *
import time

from NetClient import NetClient
from Hook import Hook
from Vector2 import Vector2
from Language import Language
from Room import Room
from Command import Command
from GameState import GameState
from Player import Player

from cl_offline import Offline
from cl_play import Play

net = NetClient()  # NetClient("127.0.0.1", 8222)
hook = Hook()
localPlayer = Player(net, hook)
room = None
concommand = Command()

# All the different game state behaviours
offline = Offline(localPlayer, concommand, hook)
play = Play(localPlayer, concommand, hook)

# Messages to put in UI
messageQueue = Queue()
commandQueue = Queue()


# Default game state
#gameState = GameState.OFFLINE
localPlayer.SetGameState(GameState.OFFLINE)


programShouldRun = True

#
#
#       UI
#
#

class UIData:
    def __init__(self):
        self.shouldClearScreen = False

uiData = UIData()
UILock = threading.Lock()

class Example(QWidget):
    global messageQueue
    global UILock
#    global shouldClearScreen
    global commandQueue

    def __init__(self):
        super().__init__()
        self.concommand = Command()

        self.chatOutput = 0
        self.userInput = 0

        self.initUI()

        self.timer = QtCore.QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.timerEvent)
        self.timer.start()
        self.timer.start(100)

    def timerEvent(self):
        if messageQueue.qsize() > 0:
            self.chatOutput.appendPlainText(messageQueue.get())
        if net.state == net.STATE_CONNECTED:
            self.setWindowTitle('Multi user Dungeon | Connected to: ' + str(net.ip) + ":" + str(net.port))
        elif net.state != net.STATE_IDLE:
            self.setWindowTitle('Multi user Dungeon | Connecting to: ' + str(net.ip) + ":" + str(net.port) + "...")
        else:
            self.setWindowTitle('Multi user Dungeon | Not connected to server')
            ''' # Doesn't work
        if uiData.shouldClearScreen:
            UILock.acquire()
            print("hello")
            del self.chatOutput
            self.chatOutput = QPlainTextEdit(self)
            self.chatOutput.setGeometry(10, 10, 580, 300)
            self.chatOutput.setReadOnly(True)
            uiData.shouldClearScreen = False
            UILock.release()
            '''

    def userInputOnUserPressedReturn(self):
        entry = self.userInput.text()

        #firstWord = concommand.StringToArgs(entry)[0]

        commandQueue.put(entry)

#        if concommand.IsCommand(firstWord):
#            concommand.Run(None, firstWord, entry)
#        else:
#            self.chatOutput.appendPlainText("Invalid command: " + firstWord)
#            self.chatOutput.appendPlainText("Type help for a list of commands.\n")

        self.userInput.setText("")


    def initUI(self):
        self.userInput = QLineEdit(self)
        self.userInput.setGeometry(10, 360, 580, 30)
        self.userInput.returnPressed.connect(self.userInputOnUserPressedReturn)

        self.chatOutput = QPlainTextEdit(self)
        self.chatOutput.setGeometry(10, 10, 580, 300)
        self.chatOutput.setReadOnly(True)

        self.setGeometry(300, 300, 600, 400)
        self.setWindowTitle('Multi user Dungeon | Not connected to server')
        self.show()

    def closeEvent(self, event):
        net.CloseConnection()
        global programShouldRun
        programShouldRun = False

#
#
#       Hooks
#
#

def ConnectedToServer(args):
    print("Connected to " + args[0] + ":" + str(args[1]))
    #messageQueue.put("Connected to " + args[0] + ":" + str(args[1]))


hook.Add("ConnectedToServer", "UI Updater", ConnectedToServer)

# Display help information to the user
def DisplayHelpText(args):
    messageQueue.put(args)


hook.Add("HelpText", "UI", DisplayHelpText)


# Display a generic list to the user
def DisplayList(args):
    messageQueue.put("List:")
    for string in args:
        messageQueue.put(string)


hook.Add("ListServers", "UI", DisplayList)


# Clear the screen -- Doesn't work - don't know how to clear qplaintextedit - docs says "TODO"
def ClearScreen(args):
    UILock.acquire()
    UIData.shouldClearScreen = True
    UILock.release()


hook.Add("ClearScreen", "UI", ClearScreen)


def BadCommandArgs(args):
    argStr = args[0]
    errorMsg = args[1]

    messageQueue.put(argStr)
    messageQueue.put(errorMsg)


hook.Add("BadCommandArgs", "UI", BadCommandArgs)


# Notify the user of any problems
def NotifyUser(args):
    messageQueue.put(args)


hook.Add("NotifyUser", "UI", NotifyUser)


#
#
#       net.Receive -- GameState PLAY
#
#

def HandleHelp(netPacket):
    print("Packet")
    messageQueue.put(netPacket.Release())


net.Receive("help", HandleHelp)


def HandleChat(netPacket):
    messageQueue.put(netPacket.Release())


net.Receive("Chat", HandleChat)


def EnteredRoom(netPacket):
    global room

    connections = netPacket.Release()
    description = netPacket.Release()

    directions = connections.split(",")
    directionVectors = []
    languageDirs = ""
    for i in range(0, len(directions)):
        coords = directions[i].split(" ")
        if len(coords) == 2:
            vec2 = Vector2(coords[0], coords[1])
            directionVectors.append(vec2)
            languageDirs += Language.ValueToWord("direction", vec2) + ","
    languageDirs = languageDirs[:-1]

    # Update our local room
    room = Room(0, directionVectors, description)

    messageQueue.put("Entered new room: \n" +
                     description + "\n" +
                     "You can move: \n" +
                     languageDirs
    )


net.Receive("EnteredRoom", EnteredRoom)


def ClearScreen(player = None, command = None, args =  None, argStr = None):
    UILock.acquire()
    uiData.shouldClearScreen = True
    UILock.release()


net.Receive("clear", ClearScreen)
#concommand.Add("clear", ClearScreen)

#
#
#       net.Receive -- GameState LOGIN
#
#

def RequestUsername():
    pass

#net.Receive()


#
#
#       net.Receive -- GameState update
#
#


def UpdateGameState(netPacket):
    global gameState
    gameState = netPacket.ReadGameState()


net.Receive("update_gamestate", UpdateGameState)


#
#
#       Commands
#
#

def ShowDirections(player, command, args, argStr):
    print("hi")
    global room

    if room is None:
        return

    languageDirs = ""
    for direction in room.connections:
        languageDirs += Language.ValueToWord("direction", direction) + ","
    languageDirs = languageDirs[:-1]

    messageQueue.put("You can move: \n" + languageDirs)


#concommand.Add("directions", ShowDirections)


def Move(player, command, args, argStr):
    global room
    direction = Language.WordToValue("direction", concommand.StringToArgs(argStr)[1])  # Remove command from string

    if direction is not None:
        print("direction!")
        if room is not None:
            print("ROOM!")
            if direction in room.connections:
                print("GO!")
                print(Language.ValueToBaseWord("direction", direction))
                net.Start("go")
                net.Write(Language.ValueToBaseWord("direction", direction))
                net.Send()
                return

    # Direction not found
    messageQueue.put("Not a valid direction: " + argStr)


#concommand.Add("go", Move)

#
#
#       Main
#
#

def ProcessInput():
    print("Resr")
    while programShouldRun:
        if commandQueue.qsize() > 0:
            argsStr = commandQueue.get()

            firstWord = concommand.StringToArgs(argsStr)[0]
            if concommand.IsCommand(firstWord):
                concommand.Run(None, firstWord, argsStr)
            else:
                messageQueue.put("Invalid command: " + firstWord)
                messageQueue.put("Type help for a list of commands.\n")

if __name__ == '__main__':


    BackgroundThread = threading.Thread(target=ProcessInput, args=())
    BackgroundThread.daemon = True
    BackgroundThread.start()


    app = QApplication(sys.argv)
    test = Example()
    hook.Run("UIFullyLoaded")
    sys.exit(app.exec_())



    #clientData.currentBackgroundThread = threading.Thread(target=backgroundThread, args=(clientData,))
   # clientData.currentBackgroundThread.start()