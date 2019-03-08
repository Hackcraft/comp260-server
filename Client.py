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

net = NetClient()
hook = Hook()

messageQueue = Queue() # messages to put in UI

class Commands:

    commands = {
        "say" : True,
        "go" : True,
        "help" : True
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
        net.Start(command)
        net.Write("".join(self.CleanUpSpaces(argStr)))
        net.Send()

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
    connections = netPacket.Release()
    description = netPacket.Release()

    directions = connections.split(",")
    languageDirs = ""
    for i in range(0, len(directions)):
        coords = directions[i].split(" ")
        if len(coords) == 2:
            vec2 = Vector2(coords[0], coords[1])
            languageDirs += Language.ValueToWord("direction", vec2) + ","
    languageDirs = languageDirs[:-1]

    messageQueue.put("Entered new room: \n" +
                     description + "\n" +
                     "You can move: \n" +
                     languageDirs
    )


net.Receive("EnteredRoom", EnteredRoom)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    test = Example()

    #clientData.currentBackgroundThread = threading.Thread(target=backgroundThread, args=(clientData,))
   # clientData.currentBackgroundThread.start()

    sys.exit(app.exec_())