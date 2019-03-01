'''
    Class which talks to clients
'''
import socket
import threading

from NetBase import NetBase
from NetPacket import NetPacket
from Hook import Hook

hook = Hook()

class NetServer(NetBase):

    serverSocket = None
    clients = {}
    clientsLock = threading.Lock()

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

    def ClientReceive(self, clientsocket):
        print("clientReceive running")
        clientValid = True
        netPacket = NetPacket()

        while clientValid == True:
            try:
                # Read the incoming data
                data = clientsocket.recv(4096)

                # Load it into a readable format
                netPacket.DecodeAndLoad(data)

                # Pass to the right Receive function
                self.RunReceiver(netPacket, clientsocket)
            except socket.error:
                print("ClientReceive - lost client");
                clientValid = False
                hook.Run("ClientLost", clientsocket)

    def AcceptClients(self, serverSocket):
        print("acceptThread running")
        while(True):
            (clientSocket, address) = serverSocket.accept()
            hook.Run("ClientJoined", clientSocket)

            thread = threading.Thread(target=self.ClientReceive, args=(clientSocket,))
            thread.start()

    def Send(self, targetSocket):
        try:
            targetSocket.send(netPacket.Encode())
        except socket.error:
            print("Failed to send data to client!")
