from Entity import Entity
from GameState import GameState


class Player(Entity):

    def __init__(self, socket, clientName = "unassigned"):
        super().__init__()
        self.tag = "player"
        self.socket = socket
        self.name = clientName
        self.isConnected = False
        self.gameState = GameState.LOGIN
        self.isAdmin = False

    def __eq__(self, otherPlayer):
        if not isinstance(otherPlayer, Player):
            return False
        return self.socket == otherPlayer.socket
