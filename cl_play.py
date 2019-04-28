'''
    Class for GameState play
'''

from cl_base import *
from Language import Language

class Play(Base):

    gameState = GameState.PLAY

    def __init__(self, *args):
        self.commands = {  # "command" = callback
            "say": self.SendNetCommand,
            "search": self.SendNetCommand,
            "help": self.Help,
            "go": self.Move()
        }

        self.hooks = {  # "eventName" = (identifier, callback)

        }
        super().__init__(*args)

    #
    # Command methods
    #

    # Generic command to server net pass through
    def SendNetCommand(self, player, command, args, argStr):
        self.net.Start(command)
        self.net.Write(argStr)
        self.net.Send()

    # Show help information on the client
    def Help(self, player, command, args, argStr):
        commands = ", ".join(self.concommand.commands)
        #messageQueue.put("The commands are: " + commands)
        self.hook.Run("ShowHelp")

    # Send movement request to the server if it's a valid move in the Language dictionary
    def Move(self, player, command, args, argStr):
        global room
        vec2 = Language.WordToValue("direction", self.concommand.StringToArgs(argStr)[1])  # Remove command from string

        if vec2 is not None:
            print("direction!")
            if room is not None:
                print("ROOM!")
                if vec2 in room.connections:
                    print("GO!")
                    print(Language.ValueToBaseWord("direction", vec2))
                    self.net.Start("go")
                    self.net.Write(Language.ValueToBaseWord("direction", vec2))
                    self.net.Send()
                    return

        # Direction not found
        #messageQueue.put("Not a valid direction: " + argStr)
        self.hook.Run("BadCommandArgs", ("Not a valid direction: " + argStr))

    #
    # Net methods
    #