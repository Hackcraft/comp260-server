import sys
import PyQt5.QtCore
import PyQt5.QtWidgets

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import QtCore
from Dungeon import Dungeon


import socket
import threading
import time

from NetClient import NetClient
net = NetClient()
clientData = net.clientData

class Example(QWidget):

    def __init__(self):
        super().__init__()

        self.chatOutput = 0
        self.userInput = 0

        self.initUI()

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.timerEvent)
        self.timer.start(100)


    def timerEvent(self):
        if clientData.incomingMessage != "":
            clientDataLock.acquire()
            self.chatOutput.appendPlainText(clientData.incomingMessage)
            clientData.incomingMessage = ""
            clientDataLock.release()

    def userInputOnUserPressedReturn(self):
        entry = self.userInput.text()
        print("User entry: "+entry)
        #clientData.serverSocket.send(bytes(entry, 'utf-8') )
        net.Start("Chat")
        net.Write(entry)
        net.Send(clientData.serverSocket)
        self.userInput.setText("")


    def initUI(self):
        self.userInput = QLineEdit(self)
        self.userInput.setGeometry(10, 360, 580, 30)
        self.userInput.returnPressed.connect(self.userInputOnUserPressedReturn)

        self.chatOutput = QPlainTextEdit(self)
        self.chatOutput.setGeometry(10, 10, 580, 300)
        self.chatOutput.setReadOnly(True)

        self.setGeometry(300, 300, 600, 400)
        self.setWindowTitle('Multi user Dungeon')
        self.show()

    def closeEvent(self, event):

        if clientData.serverSocket is not None:
            clientData.serverSocket.close()
            clientData.serverSocket = None
            clientData.connectedToServer = False
            clientData.running = False

            if clientData.currentReceivethread is not None:
                clientData.currentReceivethread.join()

            if clientData.currentBackgroundThread is not None:
                clientData.currentBackgroundThread.join()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    clientData.ex = Example()

    #clientData.currentBackgroundThread = threading.Thread(target=backgroundThread, args=(clientData,))
    #clientData.currentBackgroundThread.start()

    sys.exit(app.exec_())