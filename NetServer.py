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

    def __init__(self, ip = "127.0.0.1", port = 8222):
        if self.serverSocket == None:
            self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            # Socket availability check
            try:
                self.serverSocket.bind((ip, port))
            except socket.error:
                print("Can't start server, is another instance running?")
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
                data = clientSocket.recv(4096)

                # Load it into a readable format
                netPacket.DecodeAndLoad(data)

                # Pass to the right Receive function
                self.RunReceiver(netPacket, clientSocket)
            except socket.error:
                print("ClientReceive - lost client");
                clientValid = False

                # Make a copy of the client
                self.playersLock.acquire()
                player = self.players[clientSocket]
                self.playersLock.release()

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

            # Tell stuff they joined
            hook.Run("PlayerJoined", player)

            # Start listening for the client
            thread = threading.Thread(target=self.ClientReceive, args=(clientSocket,))
            thread.start()

    def Send(self, targetSocket):
        try:
            if type(targetSocket) is Player:
                targetSocket.socket.send(self.netPacket.Encode())
            else:
                targetSocket.send(self.netPacket.Encode())
        except socket.error:
            print("Failed to send data to client!")

    def RunReceiver(self, netPacket, clientSocket):
        self.playersLock.acquire()
        player = self.players[clientSocket]
        self.playersLock.release()

        super().RunReceiver(netPacket, player)
