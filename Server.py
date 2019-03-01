import sys
import socket
import threading

from queue import *

from Commands import *
from Dungeon import Dungeon

messageQueue = Queue()

clientIndex = 0
currentClients = {}
currentClientsLock = threading.Lock()


def clientReceive(clientsocket):
    print("clientReceive running")
    clientValid = True
    dungeon = Dungeon()# Creates new Dungeon for each user | in future use one
    while clientValid == True:
        try:
            # Read the incoming data
            data = clientsocket.recv(4096)
            inputStr = data.decode("utf-8")

            # Split by spaces
            userInput = inputStr.split(' ')
            userInput = [x for x in userInput if x != '']

            user_command = userInput[0].lower()

            if user_command == 'go':
                direction = dungeon.PhraseToDirection(userInput[1].lower())

                if dungeon.CurrentRoom().IsValidDirection(direction):
                    dungeon.MovePlayer(direction)

                    msg = "move- " + str(currentClients[clientsocket]) + " " + str(dungeon.currentRoomID)
                    currentClientsLock.acquire()
                    messageQueue.put(ClientMessage(clientsocket, msg))
                    currentClientsLock.release()

            else:
                # No command - so using chat
                currentClientsLock.acquire()
                msg = "client-" + str(currentClients[clientsocket]) + ":"
                msg += data.decode("utf-8")
                currentClientsLock.release()
                messageQueue.put(ClientMessage(clientsocket,msg))

            print("received client msg:" + inputStr);

        except socket.error:
            print("clientReceive - lost client");
            clientValid = False
            messageQueue.put(ClientLost(clientsocket))


def acceptClients(serversocket):
    print("acceptThread running")
    while(True):
        (clientsocket, address) = serversocket.accept()
        messageQueue.put(ClientJoined(clientsocket))

        thread = threading.Thread(target=clientReceive, args=(clientsocket,))
        thread.start()


def handleClientLost(command):
    currentClientsLock.acquire()
    lostClient = currentClients[command.socket]
    print("Removing lost client: client-"+str(lostClient))

    for key in currentClients:
        if key != command.socket:
            key.send(bytes("client-"+str(lostClient) + " has left the chat room", 'utf-8'))

    del currentClients[command.socket]

    currentClientsLock.release()

def handleClientJoined(command):
    global clientIndex

    currentClientsLock.acquire()
    currentClients[command.socket] = clientIndex
    clientIndex += 1

    print("Client joined: client-" + str(currentClients[command.socket]))

    outputToUser = "Welcome to chat, speak your brains here! "
    outputToUser += "Currently all you can do is type to others and use the 'go' command followed by the direction (north/east/south/west)\n"
    outputToUser += "You are: client-" + str(currentClients[command.socket]) +"\n"
    outputToUser += "Present in chat:\n"


    for key in currentClients:
        outputToUser += "client-" + str(currentClients[key]) + "\n"

    command.socket.send(bytes(outputToUser, 'utf-8') )

    for key in currentClients:
        if key != command.socket:
            key.send(bytes("client-"+str(currentClients[command.socket]) + " has joined the chat room", 'utf-8'))

    # Tell them who they are
    command.socket.send(("you- " + str(currentClients[command.socket])).encode())
    # Tell them which room to start in
    command.socket.send(("move- " + str(currentClients[command.socket]) + " 0" ).encode())

    currentClientsLock.release()

def handleClientMessage(command):
    print("client message: "+command.message)

    currentClientsLock.acquire()
    for key in currentClients:
        try:
            key.send(bytes(command.message,'utf-8'))
        except socket.error:
            messageQueue.put(ClientLost(key))

    currentClientsLock.release()

def main():
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        if len(sys.argv) > 1:
            serversocket.bind((sys.argv[1], 8222))
        else:
            serversocket.bind(("127.0.0.1", 8222))
    except socket.error:
        print("Can't start server, is another instance running?")
        exit()

    serversocket.listen(5)

    thread = threading.Thread(target=acceptClients,args=(serversocket,))
    thread.start()

    while True:

        if messageQueue.qsize()>0:
            print("Processing client commands")
            command = messageQueue.get()

            if isinstance(command, ClientJoined):
                handleClientJoined(command)

            if isinstance(command, ClientLost):
                handleClientLost(command)

            if isinstance(command, ClientMessage):
                handleClientMessage(command)


if __name__ == "__main__":
    main()