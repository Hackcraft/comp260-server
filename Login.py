from NetServer import NetServer
from NetPacket import NetPacket
from GameState import GameState
from Player import Player
from Hook import Hook


# Username and password will be sent separately


# Username:
# Account not found, would you like to create one? Yes(continue)/No(up one)
# (Send salt with password request) Password:

# To keep it modular - net.Start("Chat") should not be used here, rather the client/UI should decide what to print out


class Login:

    def __init__(self, net, hook):
        self.net = net
        self.hook = hook

        # Attach net receivers - making sure they only run when the player is in the correct Game State
        net.Receive("login_username", self.ReceieveUsername, lambda player: player.gameState is GameState.LOGIN)
        net.Receive("login_password", self.ReceivePassword, lambda player: player.gameState is GameState.LOGIN)

    def SendMessage(self, player, message):
        self.net.Start("Chat")
        self.net.Write(message)
        self.net.Send(player)

    def RequestLogin(self, player):
        self.net.Start("gamestate")
        self.net.WriteGameState(GameState.LOGIN)
        self.net.Send(player)

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

    # Checks if a username exists - if so sends salt and password request - else not found
    def ReceieveUsername(self, netPacket, player):
        username = netPacket.Release()
        canJoin = self.hook.Run("CanUserJoin", username)

        if canJoin:
            player.username = username
            player.nick = username
        else:
            self.SendMessage(player, "This user has been banned!")

    # Checks if a password matches the username - if so login success - else not correct
    def ReceivePassword(self, netPacket, player):
        # Make sure they have sent a username first
        if player.username == False:
            self.SendMessage(player, "Please send your username first.. and leave my net alone :(")
            return

        username = player.username
        password = netPacket.Release()

        # If is a valid login

        # Login with local cached/stored username and password

