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
        self.net.Receive("gamestate", self.ServerUpdatedGameState)

    def GameStateChanged(self, tupl):
        old, new = tupl

        print("OLD: " + str(old) + " NEW: " + str(new))

        if old == new:
            print("[state same] Tried to change states to the current active state")
            return

        if old == self.gameState:
            self.StopState()
            print("[state stop] Stopped: " + GameState.states[old])
        elif new == self.gameState:
            self.StartState()
            print("[state start] Started: " + GameState.states[new])

    def ServerUpdatedGameState(self, netPacket):
        gameState = netPacket.Read(GameState)

        if gameState is not None:
            self.player.SetGameState(gameState)


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
        print("Num of nets: " + str(len(self.nets.items())))
        for tag in self.nets:
            callback, condition = self.nets[tag]
            print(tag, callback, condition)
            self.net.Receive(tag, callback, condition)

    def AddCommands(self):
        print("Num of commands: " + str(len(self.commands.items())))
        for command in self.commands:
            callback = self.commands[command]
            self.concommand.Add(command, callback)

    def AddHooks(self):
        print("Num of hooks: " + str(len(self.hooks.items())))
        for eventName in self.hooks:
            identifier, callback = self.hooks[eventName]
            print(eventName, identifier, callback)
            self.hook.Add(eventName, identifier, callback)

    #
    # Stop the state and functionality
    #

    def StopState(self):
        self.RemoveNets()
        self.RemoveCommands()
        self.RemoveHooks()

    def RemoveNets(self):
        for tag in self.nets:
            callback, condition = self.nets[tag]
            self.net.RemoveReceive(tag)

    def RemoveCommands(self):
        for command in self.commands:
            self.concommand.Remove(command)

    def RemoveHooks(self):
        for eventName in self.hooks:
            print(eventName)
            identifier, callback = self.hooks[eventName]
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

