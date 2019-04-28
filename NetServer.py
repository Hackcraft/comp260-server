'''
    Class which talks to clients
'''
import socket
import threading
import warnings
import miniupnpc

from NetBase import NetBase
from NetPacket import NetPacket
from Hook import Hook
from Player import Player

hook = Hook()

# https://stackoverflow.com/a/41385033
def GetPublicIP():
    u = miniupnpc.UPnP()
    u.discoverdelay = 200
    u.discover()
    u.selectigd()
    return u.externalipaddress()

def GetLocalIP():
    u = miniupnpc.UPnP()
    u.discoverdelay = 200
    u.discover()
    u.selectigd()
    return u.lanaddr

class NetServer(NetBase):

    shouldFindClients = True
    serverSocket = None
    players = {}
    playersSinceStart = 0
    playersLock = threading.Lock()

    defaultIP = "127.0.0.1"
    defaultPort = 8222

    ip = defaultIP
    port = defaultPort
    shouldStopServer = False

    iHavePortForwarded = False

    def __init__(self, ip = None, port = None):
        if self.serverSocket == None:
            self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            hasConnection = False

            # If no ip has been provided - workout which to use
            if ip is None:

                # Try public ip
                publicSuccess = self.TryPublicSocket()

                if not publicSuccess:

                    # If our ports are likely open
                    if  self.iHavePortForwarded:

                        # Try forwarded ip (192.x.x.x)
                        print("Cannot bind to public ip. Trying forwarded ip...")

                        forwardedSuccess = self.TryForwardedSocket()

                        if not forwardedSuccess:

                            # Try local ip (127.0.0.1)
                            print("Unable to bind to forwarded. Trying 127.0.0.1")

                            localSuccess = self.TryLocalSocket()

                            if not localSuccess:
                                print("Something is really wrong. Cannot bind to any ip. Are there multiple instances?")


                    # Cannot use public ip or forwarded ip (no port forwarding)
                    else:
                        print("Unable to bind to public. Trying 127.0.0.1")
                        localSuccess = self.TryLocalSocket()

                        if not localSuccess:
                            print("Something is really wrong. Cannot bind to any ip. Are there multiple instances?")

            # If an if has been provided - try and use it
            else:
                # Socket availability check
                try:
                    if port is None:
                        self.port = self.defaultPort
                    self.serverSocket.bind((self.ip, self.port))
                    self.hasConnection = True
                except socket.error as error:
                    print("Can't start server, is another instance running?")
                    print(str(error))
                    exit()

            if self.hasConnection:
                print("Server bound to: " + self.ip + ":" + str(self.port))

            print("If you are running the server locally so are unable to connect. Launch the server with the loopback "
                      "ip as the first parameter (python3 Server.py 127.0.0.1)")

            self.serverSocket.listen(5)

            # Listen for messages
            self.acceptThread = threading.Thread(target=self.AcceptClients, args=(self.serverSocket, ))
            self.acceptThread.start() # self.acceptThread.shutdown()

    def TryPublicSocket(self):
        try:
            self.ip = GetPublicIP()
            self.port = self.defaultPort

            self.serverSocket.bind((self.ip, self.port))
            self.hasConnection = True
            return True
        except socket.error as error:
            return False

    def TryForwardedSocket(self):
        try:
            self.ip = GetLocalIP()
            self.port = self.defaultPort

            self.serverSocket.bind((self.ip, self.port))
            self.hasConnection = True
            return True
        except socket.error as error:
            return False

    def TryLocalSocket(self):
        try:
            self.ip = "127.0.0.1"
            self.port = self.defaultPort

            self.serverSocket.bind((self.ip, self.port))
            self.hasConnection = True
            return True
        except socket.error as error:
            return False

    def ClientReceive(self, clientSocket):
        print("clientReceive running")
        clientValid = True
        netPacket = NetPacket()

        while clientValid is True and not self.shouldStopServer:
            try:
                # Read the incoming data
                packetID = clientSocket.recv(4)
                packetID = packetID.decode("utf-8")

                if packetID == self.PACKET_ID:

                    dataSize = int.from_bytes(clientSocket.recv(2), "little")

                    data = clientSocket.recv(dataSize)

                    try:
                        print("Decoding")
                        # Load it into a readable format
                        netPacket.DecodeAndLoad(data)

                        print("Received")
                        print(netPacket.GetTag())

                    except:
                        pass
                    else:
                        player = self.players[clientSocket]

                        # Pass to the right Receive function
                        self.inputQueue(player, netPacket)
                        #self.RunReceiver(netPacket, player)
            except socket.error:
                print("ClientReceive - lost client");
                clientValid = False

                # Make a copy of the client
                self.playersLock.acquire()
                player = self.players[clientSocket]
                self.playersLock.release()

                # Stop their thread
#                player.thread.exit()

                # Let stuff know they left
                hook.Run("PlayerLost", player)

                # Remove the client
                self.playersLock.acquire()
                del self.players[clientSocket]
                self.playersLock.release()

    def AcceptClients(self, serverSocket):
        print("acceptThread running")
        while(self.shouldFindClients):
            try:
                (clientSocket, address) = serverSocket.accept()
            except socket.error as error:
                pass
            else:
                # Add the client and set their name
                self.playersLock.acquire()
                self.playersSinceStart += 1

                player = Player(clientSocket, "Client " + str(self.playersSinceStart))
                player.socket = clientSocket
                player.isConnected = True
                player.id = self.playersSinceStart

                self.players[clientSocket] = player
                self.playersLock.release()

                # Start listening for the client
                thread = threading.Thread(target=self.ClientReceive, args=(clientSocket,))
                thread.daemon = True
                thread.start()
                player.thread = thread

                # Tell stuff they joined
                hook.Run("PlayerJoined", player)

    def Send(self, targetSocket):
        try:
            if type(targetSocket) is Player:
                super().Send(targetSocket.socket)
            else:
                super().Send(targetSocket)
        except socket.error:
            print("Failed to send data to client!")

    def Receive(self, tag, func, condition = None):
        # Warnings
        if tag in self.receivers:
            warnings.warn("Net receiver: " + tag + " already exists!", Warning)
        if condition is None and isinstance(self, NetServer):
            warnings.warn("No condition set for net receiver: " + tag + ". Potential for exploitation!", Warning, stacklevel=2)
        # Add to the list of receivers
        self.receiversLock.acquire()
        self.receivers[tag] = (func, condition)
        self.receiversLock.release()

    def RunReceiver(self, netPacket, player):
        self.playersLock.acquire()
        player = self.players[player.socket]
        self.playersLock.release()

        super().RunReceiver(netPacket, player)

    def Stop(self):
        self.shouldFindClients = False
        self.shouldStopServer = True

        self.serverSocket.shutdown(socket.SHUT_RD)  # Shutdown, stopping any further receives
        self.serverSocket.close()

        self.acceptThread.join()

        for player in self.players:
            player.thread.join()


    def __del__(self):
        self.Stop()
