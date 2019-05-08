import time
import threading

from cl_base import Base
from GameState import GameState
from ServerList import ServerList

class Offline(Base):

    gameState = GameState.OFFLINE

    def __init__(self, *args):
        self.connectionStart = 0
        self.nets = {  # "tag" = (callback, condition)

        }

        self.commands = {  # "command" = callback
            "help": self.Help,
            "list": self.ListServers,
            "clear": self.ClearScreen,
            "connect": self.Connect
        }

        self.hooks = {  # "eventName" = (identifier, callback)
            "ServerVerificationTimeout": ("offline", self.ServerNotFound),
            "UIFullyLoaded": ("ListServers", self.ShowListAndHelp)
        }
        super().__init__(*args)
        self.ListServers()
        self.Help()

    #
    # Command methods
    #
    def Help(self, player = None, command = None, args =  None, argStr = None):
        self.hook.Run("HelpText", ("Pick a server with 'connect n' where n is the row where the name appears, "
                                   "starting from 1. Alternatively type in an ip 'connect x.x.x.x:xxxx"))

    def ListServers(self, player = None, command = None, args =  None, argStr = None):
        self.hook.Run("ListServers", (ServerList.Names()))

    def ClearScreen(self, player = None, command = None, args =  None, argStr = None):
        self.hook.Run("ClearScreen")

    def ShowListAndHelp(self, stuff):
        self.ListServers()
        self.Help()

    def Connect(self, player = None, command = None, args =  None, argStr = None):
        # Already connecting check
        if self.net.state is not GameState.OFFLINE:  # TODO Check for connected state
            self.hook.Run("BadCommandArgs", (argStr, "Currently connecting to: " + str(self.net.ip) + ":" + str(self.net.port)))

        # No args check
        if len(args) < 1:
            self.hook.Run("BadCommandArgs", (argStr, "Not a valid ip/port (format x.x.x.x:xxxx) or index 'connect n'"))
            return

        index = args[0]
        ip = None
        port = None

        # If it is an index rather than an ip
        if index.isdigit():
            index = int(index)
            servers = ServerList.Names()

            if index > 0 and index <= len(servers):
                name = servers[index-1]

                ip = ServerList.IPFromName(name)
                port = ServerList.PortFromName(name)
        else:
            # ip and port in a string - split it up
            parts = index.split(':')
            if len(parts) == 2:
                ip = parts[0]
                port = parts[1]

        # If an ip+port was extracted - try to connect to it
        if ip is not None and port is not None:
            print("Connecting... to: " + str(ip) + ":" + str(port))
            self.net.Connect(str(ip), int(port))
        else:
            self.hook.Run("BadCommandArgs", (argStr, "Not a valid ip/port (format x.x.x.x:xxxx)"))








    #
    # Hooks methods
    #
    def ServerNotFound(self, tupl):
        hello = tupl
        self.hook.Run("NotifyUser", ("Cannot connect to server: " + self.net.ip + ":" + str(self.net.port)))

    #
    # Net methods
    #