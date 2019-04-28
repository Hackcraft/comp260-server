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

class ClientData:
    def __init__(self):
        self.serverSocket = None
        self.connectedToServer = False
        self.running = True
        self.incomingMessage = ""
        self.currentBackgroundThread = None
        self.currentReceivethread = None

class NetClient(NetBase):

    clientData = ClientData()
    clientDataLock = threading.Lock()
    ip = None
    port = None
    localPlayer = True

    def __init__(self, ip = "127.0.0.1", port = 8222):
        super().__init__()
        self.ip = ip
        self.port = port
        self.backgroundThread = threading.Thread(target=self.BackgroundThread, args=(self.clientData,))
        self.backgroundThread.start()

    def ServerReceive(self, clientData):
        print("receiveThread Running")
        netPacket = NetPacket()

        while clientData.connectedToServer is True:
            try:
                # Read the incoming data
                packetID = clientData.serverSocket.recv(4)
                packetID = packetID.decode("utf-8")

                if packetID == self.PACKET_ID:

                    dataSize = int.from_bytes(clientData.serverSocket.recv(2), "little")

                    data = clientData.serverSocket.recv(dataSize)

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
                clientData.connectedToServer = False
                clientData.serverSocket = None

    def BackgroundThread(self, clientData):
        print("backgroundThread running")
        clientData.connectedToServer = False

        while (clientData.connectedToServer is False) and (clientData.running is True):
            try:
                if clientData.serverSocket is None:
                    clientData.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

                if clientData.serverSocket is not None:
                    clientData.serverSocket.connect((self.ip, self.port))

                # Connected to server - create localPlayer
                self.localPlayer = Player(clientData.serverSocket, self)
                self.hasConnection = True

                clientData.connectedToServer = True
                clientData.receiveThread = threading.Thread(target=self.ServerReceive, args=(self.clientData,))
                clientData.receiveThread.start()

                print("connected")
                hook.Run("ConnectedToServer", (self.ip, self.port))

                while clientData.connectedToServer is True:
                    time.sleep(1.0)

            except socket.error:
                print("no connection")
                time.sleep(1)
                #self.clientDataLock.acquire()
                #self.clientDataLock.release()

    def Send(self):
        try:
            super().Send(self.clientData.serverSocket)
            print("Sending: " + self.netPacket.GetTag())
        except socket.error:
            print("Failed to send data to server!")

    def CloseConnection(self):
        if self.clientData.serverSocket is not None:
            self.clientData.serverSocket.close()
            self.clientData.serverSocket = None
            self.clientData.connectedToServer = False
            self.clientData.running = False

            if self.clientData.currentReceivethread is not None:
                self.clientData.currentReceivethread.join()

            if self.clientData.currentBackgroundThread is not None:
                self.clientData.currentBackgroundThread.join()