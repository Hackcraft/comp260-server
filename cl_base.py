'''
    Base class for GameState execution classes
'''

from NetClient import NetClient
from Command import Command
from Hook import Hook
from GameState import GameState


class Base:

    gameState = None

    #nets = {}  # "tag" = (callback, condition)
    #commands = {}  # "command" = callback
    #hooks = {}  # "eventName" = (identifier, callback)

    def __init__(self, player, concommand, hook):
        self.player = player
        self.net = player.net
        self.concommand = concommand
        self.hook = hook

        if self.nets is None:
            self.nets = {}

        if self.commands is None:
            self.commands = {}

        if self.hooks is None:
            self.hooks = {}

        self.hook.Add("GameStateChanged", self.__class__.__name__, self.GameStateChanged)

    def GameStateChanged(self, tupl):
        old, new = tupl

        if old == new:
            print("[state same] Tried to change states to the current active state")
            return

        if old == self.gameState:
            self.StopState()
            print("[state stop] Stopped: " + GameState.states[old])
        elif new == self.gameState:
            self.StartState()
            print("[state start] Started: " + GameState.states[new])


    #
    # Start the state and functionality
    #

    def StartState(self):
        # Update the players gameState
        self.player.gameState = self.gameState

        self.AddNets()
        self.AddCommands()
        self.AddHooks()

    def AddNets(self):
        print("Num of commands: " + str(len(self.nets.items())))
        for tag, tupl in self.nets.items():
            callback, condition = tupl
            self.net.Receive(tag, callback, condition)

    def AddCommands(self):
        for command, callback in self.commands.items():
            self.concommand.Add(command, callback)

    def AddHooks(self):
        for eventName, tupl in self.hooks.items():
            identifier, callback = tupl
            self.hook.Add(eventName, identifier, callback)

    #
    # Stop the state and functionality
    #

    def StopState(self):
        self.RemoveCommands()
        self.RemoveHooks()
        self.RemoveNets()

    def RemoveNets(self):
        for tag, tupl in self.nets.items():
            callback, condition = tupl
            self.net.RemoveReceive(tag)

    def RemoveCommands(self):
        for command, callback in self.commands.items():
            self.concommand.Remove(command)

    def RemoveHooks(self):
        for eventName, tupl in self.hooks.items():
            print(eventName)
            print(tupl)
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