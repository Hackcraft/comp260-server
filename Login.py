from NetServer import NetServer
from NetPacket import NetPacket
from GameState import GameState
from Player import Player
from Hook import Hook

def ReceiveLogin(netPakcet, player):
    username = netPakcet.Release()
    password = netPakcet.Release()





class Login:

    def __init__(self, net, hook):
        self.net = net
        hook.Add("PlayerSay", "Login", self.VerifyUsernname) # Not what I want... say ... != raw input
        hook.Add("PlayerSay", "Login", self.VerifyPassword)

    def RequestLogin(self, player):
        print("Login")

        self.net.Start("Chat")
        self.net.Write("Please type your username:")
        self.net.Send(player)

    def HandlePlayerinput(self):
        pass

    def VerifyUsernname(player, message):
        pass

    def VerifyPassword():
        pass


