from Entity import Entity

class Player(Entity):

    def __init__(self, socket, clientName = "unassigned"):
        super().__init__()
        self.tag = "player"
        self.socket = socket
        self.name = clientName
        self.isConnected = False

    def __eq__(self, otherPlayer):
        if not isinstance(otherPlayer, Player):
            return False
        return self.socket == otherPlayer.socket
