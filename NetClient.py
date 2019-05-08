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
from Encryption import Encryption
from GameState import GameState

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

    privateKey = None
    socketPublicKey = None

    # Time in seconds to wait for a response from the server
    verifyTimeout = 5
    verifyStartTime = 0
    connectionCheckThread = None

    def __init__(self):
        super().__init__()
        self.state = GameState.OFFLINE
        self.Receive("Verified", self.ServerValidated)

    def Connect(self, ip = "127.0.0.1", port = 8222):
        # Stop any existing connections
        self.CloseConnection()

        # Update the state
        self.state = GameState.OFFLINE

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
                        # If there's a private key assigned to the socket, decrypt the data!
                        print(data)
#                        if self.privateKey is not None and self.state >= GameState.LOGIN:
#                            decrypted = self.encrypt.Decrypt(self.privateKey, data)
##                            if decrypted is not None:
#                                data = decrypted
#                                print("Decrypted message")
                        
                        print("Decoding")
                        # Load it into a readable format
                        netPacket.DecodeAndLoad(data)

                        print("Received")
                        print(netPacket.GetTag())
                    except Exception as e:
                        print(e)
                        print("Server sent data which made no sense!")
                        pass
                    else:
                        self.RunReceiver(netPacket, None)
            except socket.error:
                self.state = GameState.OFFLINE
                print("Server lost")
                self.hasConnection = False
                hook.Run("DisconnectedFromServer", (self.ip, self.port))
                self.connectedToServer = False
                self.serverSocket = None
                self.socketPublicKey = None

    def BackgroundThread(self):
        print("backgroundThread running")
        self.connectedToServer = False
        runningTimeout = False

        while self.state is GameState.OFFLINE:
            try:
                if self.serverSocket is None:
                    self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

                if self.serverSocket is not None:
                    self.serverSocket.connect((self.ip, self.port))

            except socket.error as error:
                #print(error)
                pass
                #time.sleep(1)
                #self.clientDataLock.acquire()
                #self.clientDataLock.release()
            else:
                print("Found ip")
                self.connectedToServer = True
                self.state = GameState.KEY_EXCHANGE
                self.receiveThread = threading.Thread(target=self.ServerReceive, args=())
                self.receiveThread.start()

                self.verifyStartTime = time.time()
                self.CheckConnectionAfterDelay()


    def CheckConnectionAfterDelay(self):
        self.connectionCheckThread = threading.Thread(target=self.DelayedConnectionCheck, args=())
        self.connectionCheckThread.start()

        # Convert our public key to pem
        publicKey = self.encrypt.GetPublicKey(self.privateKey)
        pemKey = self.encrypt.ExportKey(publicKey)

        # Send verification request
        self.Start("Verify")
        self.Write(pemKey)
        self.Send()

        print("Asking server to verify if it is a MUD server")
        print("Sending public key")


    def DelayedConnectionCheck(self):
        time.sleep(self.verifyTimeout)
        # If it took too long (server didn't respond)
        if self.state < GameState.LOGIN and time.time() - self.verifyStartTime >= self.verifyTimeout:
            self.state = GameState.OFFLINE
            hook.Run("ServerVerificationTimeout", (self.ip, self.port))
            self.socketPublicKey = None


    def ServerValidated(self, netPacket):
        # load pem public key
        data = netPacket.Release()
        if data is None:
            return
        
        key = self.encrypt.ImportKey(data)
        
        # Stop if no public key
        if key is None:
            print("Client sent invalid public key!")
            return
            
        # We have a key!
        self.socketPublicKey = key
        
        self.state = GameState.LOGIN
        self.connectedToServer = True
        
        print("Server verified")
        print("Key received from server")

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
            self.socketPublicKey = None

            if self.receiveThread is not None:
                self.receiveThread.join()

            if self.backgroundThread is not None:
                self.backgroundThread.join()