'''
	Class to run functions off events
'''

import threading
from Language import Language

class Command:

    commands = {}
    commandsLock = threading.Lock()

    def __init__(self):
        pass

    def Add(self, command, callback):
        self.commandsLock.acquire()
        self.commands[command] = callback
        self.commandsLock.release()

    def Run(self, player, command, argsStr):
        self.commandsLock.acquire()
        if command in self.commands:
            args = self.StringToArgs(argsStr)
            args.pop(0)  # Remove command from args
            self.commands[command](player, command, args, argsStr)
        elif self.IsInOtherLanguage(command):
            args = self.StringToArgs(argsStr)
            args.pop(0)  # Remove command from args
            self.commands[command](player, self.GetInOtherLanguage(command), args, argsStr)

        self.commandsLock.release()

    def IsCommand(self, command):
        return command in self.commands

    def IsInOtherLanguage(self, command):
        return self.GetInOtherLanguage(command) is not None

    def GetInOtherLanguage(self, command):
        commandValue = Language.WordToValue("command", command)
        if commandValue is not None:
            baseCommand = Language.ValueToBaseWord("command", commandValue)
            if baseCommand is not None and baseCommand in self.commands:
                return baseCommand
        return None

    def StringToArgs(self, argStr):
        separatedStrings = argStr.split(' ')
        trimmedStrings = [x for x in separatedStrings if x != '']
        return trimmedStrings

    def Remove(self, commandName):
        self.commandsLock.acquire()
        if commandName in self.commands:
            self.commands[commandName] = None
        self.commandsLock.release()

