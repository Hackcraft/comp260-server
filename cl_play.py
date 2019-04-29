'''
    Class for GameState play
'''

from cl_base import *
from Language import Language
from Player import Player
from Vector2 import Vector2
from Room import Room

class Play(Base):

    gameState = GameState.PLAY
    room = None

    def __init__(self, *args):
        self.nets = {  # "tag" = (callback, condition)
            "EnteredRoom": (self.EnteredRoom, None),
            "Chat": (self.ReceiveChat, None),
            "help": (self.ReceiveHelp, None),
            "directions": (self.ShowDirections, None),
        }

        self.commands = {  # "command" = callback
            "say": self.SendNetCommand,
            "search": self.SendNetCommand,
            "help": self.Help,
            "go": self.Move,

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
        vec2 = Language.WordToValue("direction", self.concommand.StringToArgs(argStr)[1])  # Remove command from string

        if vec2 is not None:
            print("direction!")
            if self.room is not None:
                print("ROOM!")
                if vec2 in self.room.connections:
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

    def EnteredRoom(self, netPacket):
        connections = netPacket.Release()
        description = netPacket.Release()

        directions = connections.split(",")
        directionVectors = []
        languageDirs = ""
        for i in range(0, len(directions)):
            coords = directions[i].split(" ")
            if len(coords) == 2:
                vec2 = Vector2(coords[0], coords[1])
                directionVectors.append(vec2)
                languageDirs += Language.ValueToWord("direction", vec2) + ","
        languageDirs = languageDirs[:-1]

        # Update our local room
        self.room = Room(0, directionVectors, description)

        self.hook.Run("NotifyUser", "EnteredRoom","Entered new room: \n" +
                         description + "\n" +
                         "You can move: \n" +
                         languageDirs
                         )

    def ShowDirections(self, player, command, args, argStr):
        if self.room is None:
            return

        languageDirs = ""
        for direction in self.room.connections:
            languageDirs += Language.ValueToWord("direction", direction) + ","
        languageDirs = languageDirs[:-1]

        self.hook.Run("NotifyUser", "You can move: \n" + languageDirs)

    def ReceiveChat(self, netPacket):
        self.hook.Run("NotifyUser", netPacket.Release())

    def ReceiveHelp(self, netPacket):
        self.hook.Run("NotifyUser", netPacket.Release())