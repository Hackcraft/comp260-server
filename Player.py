from Entity import Entity
from GameState import GameState

class Player(Entity):

    def __init__(self, socket, net, clientName = "unassigned"):
        super().__init__()
        self.username = False
        self.tag = "player"
        self.socket = socket
        self.nick = clientName
        self.isConnected = False
        self.gameState = GameState.LOGIN
        self.isAdmin = False
        self.isLocalPlayer = False
        self.net = None


    def __eq__(self, otherPlayer):
        if not isinstance(otherPlayer, Player):
            return False
        return self.socket == otherPlayer.socket

    def SetGameState(self, gameState):
        if self.isLocalPlayer:
            self.gameState = gameState
        else:
            self.net.Start("gamestate")
            self.net.WriteGameState(gameState)
            self.net.Send()
#
#    def SetNet(self, net, isServerside):
#        self.isLocalPlayer = not isServerside
#        self.net = net

    def IsLocalPlayer(self):
        if self.net is not None:
            if self.net.localPlayer is not False:
                return True
        return False

    def IsValid(self):
        if self.net is not None:
            if self.net.self.hasConnection and self.socket is not None:
                return True
        return False