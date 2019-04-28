'''
    Class which talks to server
'''
import time
import threading
import socket

from NetBase import NetBase
from NetPacket import NetPacket
from Hook import Hook
from Player import Player

hook = Hook()

class NetClient(NetBase):

    clientDataLock = threading.Lock()
    ip = None
    port = None
    localPlayer = True

    serverSocket = None
    connectedToServer = False
    running = True
    incomingMessage = ""
    backgroundThread = None
    receiveThread = None

    def __init__(self, ip = "127.0.0.1", port = 8222):
        super().__init__()
        self.ip = ip
        self.port = port
        self.backgroundThread = threading.Thread(target=self.BackgroundThread, args=(self,))
        self.backgroundThread.start()

    def ServerReceive(self):
        print("receiveThread Running")
        netPacket = NetPacket()

        while self.connectedToServer is True:
            try:
                # Read the incoming data
                packetID = self.serverSocket.recv(4)
                packetID = packetID.decode("utf-8")

                if packetID == self.PACKET_ID:

                    dataSize = int.from_bytes(self.serverSocket.recv(2), "little")

                    data = self.serverSocket.recv(dataSize)

                    try:
                        print("Decoding")
                        # Load it into a readable format
                        netPacket.DecodeAndLoad(data)

                        print("Received")
                        print(netPacket.GetTag())
                    except:
                        print("Server sent data which made no sense!")
                        pass
                    else:
                        self.RunReceiver(netPacket, None)
            except socket.error:
                print("Server lost")
                self.hasConnection = False
                hook.Run("DisconnectedFromServer", (self.ip, self.port))
                self.connectedToServer = False
                self.serverSocket = None

    def BackgroundThread(self):
        print("backgroundThread running")
        self.connectedToServer = False

        while (self.connectedToServer is False) and (self.running is True):
            try:
                if self.serverSocket is None:
                    self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

                if self.serverSocket is not None:
                    self.serverSocket.connect((self.ip, self.port))

                # Connected to server - create localPlayer
                self.localPlayer = Player(self.serverSocket, self)
                self.hasConnection = True

                self.connectedToServer = True
                self.receiveThread = threading.Thread(target=self.ServerReceive, args=(self,))
                self.receiveThread.start()

                print("connected")
                hook.Run("ConnectedToServer", (self.ip, self.port))

                while self.connectedToServer is True:
                    time.sleep(1.0)

            except socket.error:
                print("no connection")
                time.sleep(1)
                #self.clientDataLock.acquire()
                #self.clientDataLock.release()

    def Send(self):
        try:
            super().Send(self.serverSocket)
            print("Sending: " + self.netPacket.GetTag())
        except socket.error:
            print("Failed to send data to server!")

    def CloseConnection(self):
        if self.serverSocket is not None:
            self.serverSocket.close()
            self.serverSocket = None
            self.connectedToServer = False
            self.running = False

            if self.receiveThread is not None:
                self.receiveThread.join()

            if self.backgroundThread is not None:
                self.backgroundThread.join()