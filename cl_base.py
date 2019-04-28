'''
    Base class for GameState execution classes
'''

from NetClient import NetClient
from Command import Command
from Hook import Hook
from GameState import GameState


class Base:

    gameState = None

    nets = {  # "tag" = (callback, condition)

    }

    commands = {  # "command" = callback

    }

    hooks = {  # "eventName" = (identifier, callback)

    }

    def __init__(self, player, concommand, hook):
        self.player = player
        self.net = player.net
        self.concommand = concommand
        self.hook = hook

    #
    # Start the state and functionality
    #

    def StartState(self, player):
        # Update the players gameState
        player.gameState = self.gameState

        self.AddNets()
        self.AddCommands()
        self.AddHooks()

    def AddNets(self):
        for tag, tupl in self.commands.items():
            callback, condition = tupl
            self.net.Receive(tag, callback, condition)

    def AddCommands(self):
        for command, callback in self.commands.items():
            self.concommand.Add(command, callback)

    def AddHooks(self):
        for eventName, tupl in self.commands.items():
            identifier, callback = tupl
            self.hook.Add(eventName, identifier, callback)

    #
    # Stop the state and functionality
    #

    def StopState(self, player):
        self.RemoveCommands()
        self.RemoveHooks()
        self.RemoveNets()

    def RemoveNets(self):
        for tag, tupl in self.commands.items():
            callback, condition = tupl
            self.net.RemoveReceive(tag)

    def RemoveCommands(self):
        for command, callback in self.commands.items():
            self.concommand.Remove(command)

    def RemoveHooks(self):
        for eventName, tupl in self.commands.items():
            identifier, callback = tupl
            self.hook.Remove(eventName, identifier)

    #
    # Command methods
    #

    #
    # Hooks methods
    #

    #
    # Net methods
    #