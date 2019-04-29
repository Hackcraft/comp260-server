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

    # States
    STATE_IDLE = 0
    STATE_CONNECT = 1
    STATE_VERIFY = 2
    STATE_CONNECTED = 3

    # Time in seconds to wait for a response from the server
    verifyTimeout = 2
    verifyStartTime = 0
    connectionCheckThread = None

    def __init__(self):
        self.state = self.STATE_IDLE
        self.Receive("Verified", self.ServerValidated)
        super().__init__()

    def Connect(self, ip = "127.0.0.1", port = 8222):
        # Stop any existing connections
        self.CloseConnection()

        # Update the state
        self.state = self.STATE_CONNECT

        # Update the new ip + port
        self.ip = ip
        self.port = port
#        self.running = True

        # Setup the socket
        self.backgroundThread = threading.Thread(target=self.BackgroundThread, args=())
        self.backgroundThread.start()

    def Disconnect(self):
        self.running = False
        self.CloseConnection()

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
                self.state = self.STATE_IDLE
                print("Server lost")
                self.hasConnection = False
                hook.Run("DisconnectedFromServer", (self.ip, self.port))
                self.connectedToServer = False
                self.serverSocket = None

    def BackgroundThread(self):
        print("backgroundThread running")
        self.connectedToServer = False
        runningTimeout = False

        while self.state is self.STATE_CONNECT:
            try:
                if self.serverSocket is None:
                    self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

                if self.serverSocket is not None:
                    self.serverSocket.connect((self.ip, self.port))

                #print(self.ip, str(self.port))

                # Validate the server is running the server

                # Connected to server - create localPlayer TODO use Player from client
#                self.localPlayer = Player(self.serverSocket, self)
#                self.hasConnection = True

                self.connectedToServer = True
                self.receiveThread = threading.Thread(target=self.ServerReceive, args=())
                self.receiveThread.start()

                #print("connected")
                #hook.Run("ConnectedToServer", (self.ip, self.port))

            except socket.error:
                pass
                #time.sleep(1)
                #self.clientDataLock.acquire()
                #self.clientDataLock.release()

            if not runningTimeout and self.state is not self.STATE_CONNECTED:
                self.verifyStartTime = time.time()
                self.CheckConnectionAfterDelay()

    def CheckConnectionAfterDelay(self):
        self.connectionCheckThread = threading.Thread(target=self.DelayedConnectionCheck, args=())
        self.state = self.STATE_VERIFY
        self.connectionCheckThread.start()

        # Send verification request
        self.Start("Verify")
        self.Send()
        print("Asking server to verify if it is a MUD server")


    def DelayedConnectionCheck(self):
        time.sleep(self.verifyTimeout)
        # If it took too long (server didn't respond)
        if self.state == self.STATE_VERIFY and time.time() - self.verifyStartTime >= self.verifyTimeout:
            self.state = self.STATE_IDLE
            hook.Run("ServerVerificationTimeout", (self.ip, self.port))


    def ServerValidated(self, netpacket):
        self.state = self.STATE_CONNECTED
        self.connectedToServer = True
        hook.Run("ConnectedToServer", (self.ip, self.port))


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