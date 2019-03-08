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

net = NetClient()
hook = Hook()
room = None

messageQueue = Queue() # messages to put in UI

class Commands:

    NET_COMMAND = "RunNetCommand"
    LOCAL_COMMAND = "RunLocalCommand"

    commands = {
        "say" : NET_COMMAND,
        "help": NET_COMMAND,

        "directions": LOCAL_COMMAND,
        "go": LOCAL_COMMAND
    }

    def GetFirstWord(self, string = ""):
        userInput = self.SplitUpString(string)
        return userInput[0]

    def GetAllButFirstWord(self, string):
        userInput = self.SplitUpString(string)
        userInput.pop(0)
        return " ".join(userInput)

    def SplitUpString(self, string):
        string = string.split(' ')
        string = self.CleanUpSpaces(string)
        return string

    def CleanUpSpaces(self, string):
        return [x for x in string if x != '']

    def IsCommand(self, command):
        return command in self.commands

    def Execute(self, command, argStr = ""):
        if self.commands[command] == self.NET_COMMAND:
            self.RunNetCommand(command, argStr)
        elif self.commands[command] == self.LOCAL_COMMAND:
            self.RunLocalCommand(command, argStr)

    def RunNetCommand(self, command, argStr = ""):
        net.Start(command)
        net.Write("".join(self.CleanUpSpaces(argStr)))
        net.Send()

    def RunLocalCommand(self, command, argStr = ""):
        hook.Run("RunLocalCommand_" + command, argStr)

class Example(QWidget):

    commands = Commands()
    global messageQueue

    def __init__(self):
        super().__init__()

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

    def userInputOnUserPressedReturn(self):
        entry = self.userInput.text()

        print("here")
        command = self.commands.GetFirstWord(entry)
        print("GetFirstWord")

        if self.commands.IsCommand(command):
            print("IsCommand")
            argStr = self.commands.GetAllButFirstWord(entry)
            print("GetAllButFirstWord")
            self.commands.Execute(command, argStr)
            print("Execute")
        else:
            self.chatOutput.appendPlainText("Invalid command: " + command)
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

    def HandleHelp(self, netPacket):
        self.currentMessageLock.acquire()
        self.currentMessage = netPacket.Release()
        self.currentMessageLock.release()

    net.Receive("help", HandleHelp)

def ConnectedToServer(args):
    print("Connected to " + args[0] + ":" + str(args[1]))
    messageQueue.put("Connected to " + args[0] + ":" + str(args[1]))


hook.Add("ConnectedToServer", "UI Updater", ConnectedToServer)

def HandleHelp(netPacket):
    print("Packet")
    messageQueue.put(netPacket.Release())  # release is weird


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


def ShowDirections(argStr):
    print("hi")
    global room

    if room is None:
        return

    languageDirs = ""
    for direction in room.connections:
        languageDirs += Language.ValueToWord("direction", direction) + ","
    languageDirs = languageDirs[:-1]

    messageQueue.put("You can move: \n" + languageDirs)


hook.Add("RunLocalCommand_" + "directions", "ShowDirections", ShowDirections)


def Move(argStr):
    global room

    direction = Language.WordToValue("direction", argStr)

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


hook.Add("RunLocalCommand_" + "go", "MoveLocalPlayer", Move)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    test = Example()

    #clientData.currentBackgroundThread = threading.Thread(target=backgroundThread, args=(clientData,))
   # clientData.currentBackgroundThread.start()

    sys.exit(app.exec_())