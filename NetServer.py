'''
	Class which talks to clients
'''

# Accept clients
clients = {}
clientsLock = threading.Lock()

def acceptThread(serverSocket):
    while True:
        newClient = serverSocket.accept()

        try:
            data = newClient[0].recv(4096)
            isConnected = True
        except socket.error:
            isConnected = False

        if isConnected:
            print("Added client!")
            clientsLock.acquire()
            clients[newClient[0]] = 0
            clientsLock.release()

class NetServer(NetBase):

	def __init__(self, ip = "127.0.0.1", port = 8222):
		self.mySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.mySocket.bind((ip, port))
		self.mySocket.listen(5)

		self.myThread = threading.Thread(target=acceptThread, args=(mySocket, ))
		self.myThread.start()

