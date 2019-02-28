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


class ClientData:
    def __init__(self):
        self.serverSocket = None
        self.connectedToServer = False
        self.running = True
        self.incomingMessage = ""
        self.currentBackgroundThread = None
        self.currentReceivethread = None


clientData = ClientData()
clientDataLock = threading.Lock()
clientID = None
roomID = None
dungeon = Dungeon()

def receiveThread(clientData):
    print("receiveThread running")
    global clientID

    while clientData.connectedToServer is True:
        try:
            data = clientData.serverSocket.recv(4096)
            text = ""
            text += data.decode("utf-8")

            testSplit = text.split(' ')

            # Assign client id to client
            if clientID is None and testSplit[0].lower() == "you-":
                clientID = testSplit[1].lower()

            elif testSplit[0].lower() == "move-":
                otherClientID = testSplit[1]
                otherRoomID = testSplit[2]


                # If another client
                if otherClientID != clientID:
                    if otherRoomID == roomID:
                        clientDataLock.acquire()
                        clientData.incomingMessage += str(otherClientID) + " has entered your room."
                        clientDataLock.release()

                else:
                    roomID = otherRoomID

                    roomData = dungeon.roomMap[int(roomID)]
                    clientDataLock.acquire()
                    clientData.incomingMessage += roomData.Description() + "\nDirections: " + roomData.DirectionsParser()
                    clientDataLock.release()



            else:
                clientDataLock.acquire()
                clientData.incomingMessage += text
                clientDataLock.release()
                print(text)
        except socket.error:
            print("Server lost")
            clientData.connectedToServer = False
            clientData.serverSocket = None

def backgroundThread(clientData):
    print("backgroundThread running")
    clientData.connectedToServer = False

    while (clientData.connectedToServer is False) and (clientData.running is True):
        try:

            if clientData.serverSocket is None:
                clientData.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            if clientData.serverSocket is not None:
                clientData.serverSocket.connect(("127.0.0.1", 8222))

            clientData.connectedToServer = True
            clientData.currentReceivethread = threading.Thread(target=receiveThread, args=(clientData,))
            clientData.currentReceivethread.start()

            print("connected")

            while clientData.connectedToServer is True:
                time.sleep(1.0)

        except socket.error:
            print("no connection")
            time.sleep(1)
            clientDataLock.acquire()
            clientData.incomingMessage = "\nNoServer"
            clientDataLock.release()

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
        clientData.serverSocket.send(bytes(entry, 'utf-8') )
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

    clientData.currentBackgroundThread = threading.Thread(target=backgroundThread, args=(clientData,))
    clientData.currentBackgroundThread.start()

    sys.exit(app.exec_())