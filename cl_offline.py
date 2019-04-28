from cl_base import Base
from GameState import GameState
from ServerList import ServerList

class Offline(Base):

    gameState = GameState.OFFLINE

    def __init__(self, *args):
        self.nets = {  # "tag" = (callback, condition)

        }

        self.commands = {  # "command" = callback
            "help": self.Help,
            "list": self.ListServers,
            "clear": self.ClearScreen
        }

        self.hooks = {  # "eventName" = (identifier, callback)

        }
        super().__init__(*args)
        self.ListServers()
        self.Help()

    #
    # Command methods
    #
    def Help(self):
        self.hook.Run("HelpText", ("Pick a server with 'connect n' where n is the row where the name appears, starting from 1."))

    def ListServers(self):
        self.hook.Run("ListServers", (ServerList.Names()))

    def ClearScreen(self):
        self.hook.Run("ClearScreen")

    #
    # Hooks methods
    #

    #
    # Net methods
    #