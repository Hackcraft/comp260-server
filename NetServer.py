'''
    Class which talks to clients
'''
import socket
import threading

from NetBase import NetBase
from NetPacket import NetPacket
from Hook import Hook
from Player import Player

hook = Hook()

class NetServer(NetBase):

    serverSocket = None
    players = {}
    playersSinceStart = 0
    playersLock = threading.Lock()

    defaultIP = "127.0.0.1"
    defaultPort = 8222

    def __init__(self, ip = "127.0.0.1", port = 8222):
        if self.serverSocket == None:
            self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            # Socket availability check
            try:
                self.serverSocket.bind((ip, port))
            except socket.error as error:
                print("Can't start server, is another instance running?")
                print(str(error))
                exit()

            self.serverSocket.listen(5)

            # Listen for messages
            self.acceptThread = threading.Thread(target=self.AcceptClients, args=(self.serverSocket, ))
            self.acceptThread.start() # self.acceptThread.shutdown()

    def ClientReceive(self, clientSocket):
        print("clientReceive running")
        clientValid = True
        netPacket = NetPacket()

        while clientValid == True:
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
                        # Pass to the right Receive function
                        self.RunReceiver(netPacket, clientSocket)
            except socket.error:
                print("ClientReceive - lost client");
                clientValid = False

                # Make a copy of the client
                self.playersLock.acquire()
                player = self.players[clientSocket]
                self.playersLock.release()

                # Stop their thread
                player.thread.shutdown()

                # Let stuff know they left
                hook.Run("PlayerLost", player)

                # Remove the client
                self.playersLock.acquire()
                del self.players[clientSocket]
                self.playersLock.release()

    def AcceptClients(self, serverSocket):
        print("acceptThread running")
        while(True):
            (clientSocket, address) = serverSocket.accept()

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

    def RunReceiver(self, netPacket, clientSocket):
        self.playersLock.acquire()
        player = self.players[clientSocket]
        self.playersLock.release()

        super().RunReceiver(netPacket, player)

    def Stop(self):
        self.serverSocket.shutdown(self.serverSocket.SHUT_RD)  # Shutdown, stopping any further receives
        self.serverSocket.close()

        self.acceptThread.shutdown()
