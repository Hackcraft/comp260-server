from Entity import Entity

class Player(Entity):

    def __init__(self, clientSocket, clientName = "unassigned"):
        super().__init__()
        self.SetTag("player")
        self.clientSocket = clientSocket
        self.name = clientName

    def GetName(self):
    	return str(self.name)
