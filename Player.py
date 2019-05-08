from Entity import Entity
from GameState import GameState

class Player(Entity):

    def __init__(self, net, hook = None, clientName = "unassigned"):
        super().__init__()
        self.username = False
        self.tag = "player"
        self.socket = None
        self.nick = clientName
        self.isConnected = False
        self.gameState = None
        self.isAdmin = False
#        self.isLocalPlayer = False
        self.net = net
        self.hook = hook
        self.room = None
        self.socketPublicKey = None
        print("Creating new player")

    def __eq__(self, otherPlayer):
        if not isinstance(otherPlayer, Player):
            return False
        return self.socket == otherPlayer.socket

    def SetGameState(self, gameState):
        print("Setting gamestate to: " + GameState.states[gameState])
        if self.IsLocalPlayer():
            old = self.gameState
            self.gameState = gameState
            self.hook.Run("GameStateChanged", (old, gameState))
        else:
            self.gameState = gameState
            self.hook.Run("GameStateChanged", (player, old, gameState))
            self.net.Start("gamestate")
            self.net.Write(GameState, gameState)
            self.net.Send(self)
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