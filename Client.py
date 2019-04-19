import sys
import PyQt5.QtCore
import PyQt5.QtWidgets

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import QtCore
from Dungeon import Dungeon


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

net = NetClient("127.0.0.1", 8222)
hook = Hook()
room = None
concommand = Command()

messageQueue = Queue() # messages to put in UI

#
#
#       UI
#
#

class Example(QWidget):
    global messageQueue

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
        if net.clientData.connectedToServer:
            self.setWindowTitle('Multi user Dungeon | Connected to: ' + str(net.ip) + ":" + str(net.port))
        else:
            self.setWindowTitle('Multi user Dungeon | Not connected to server')

    def userInputOnUserPressedReturn(self):
        entry = self.userInput.text()

        firstWord = concommand.StringToArgs(entry)[0]

        if concommand.IsCommand(firstWord):
            concommand.Run(None, firstWord, entry)
        else:
            self.chatOutput.appendPlainText("Invalid command: " + firstWord)
            self.chatOutput.appendPlainText("Type help for a list of commands.\n")

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

#
#
#       Hooks
#
#

def ConnectedToServer(args):
    print("Connected to " + args[0] + ":" + str(args[1]))
    messageQueue.put("Connected to " + args[0] + ":" + str(args[1]))


hook.Add("ConnectedToServer", "UI Updater", ConnectedToServer)

#
#
#       net.Receive
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


concommand.Add("directions", ShowDirections)


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


concommand.Add("go", Move)


def Help(player, command, args, argStr):
    commands = ", ".join(concommand.commands)
    messageQueue.put("The commands are: " + commands)


concommand.Add("help", Help)


def SendNetCommand(player, command, args, argStr):
    net.Start(command)
    net.Write(argStr)
    net.Send()


concommand.Add("say", SendNetCommand)
concommand.Add("search", SendNetCommand)

#
#
#       Main
#
#

if __name__ == '__main__':
    app = QApplication(sys.argv)
    test = Example()

    #clientData.currentBackgroundThread = threading.Thread(target=backgroundThread, args=(clientData,))
   # clientData.currentBackgroundThread.start()

    sys.exit(app.exec_())