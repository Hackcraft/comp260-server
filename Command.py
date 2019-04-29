'''
	Class to run functions off events
'''

import threading
from Language import Language

class Command:

    commands = {}
    commandsLock = threading.RLock()

    def __init__(self):
        pass

    def Add(self, command, callback):
        if callback is None:
            print("Error adding: '" + command + "' no callback passed!")
        else:
            with self.commandsLock:
                self.commands[command] = callback
            print("[command add] Added: " + command)

    def Run(self, player, command, argsStr):
        with self.commandsLock:
            if command in self.commands:
                args = self.StringToArgs(argsStr)
                args.pop(0)  # Remove command from args
                if args is None:
                    args = ""
                self.commands[command](player, command, args, argsStr)
                print("[command run] Ran: " + command)
            elif self.IsInOtherLanguage(command):
                args = self.StringToArgs(argsStr)
                args.pop(0)  # Remove command from args
                self.commands[command](player, self.GetInOtherLanguage(command), args, argsStr)
                print("[command run] Ran: " + command)

    def IsCommand(self, command):
        with self.commandsLock:
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
        with self.commandsLock:
            if commandName in self.commands:
                del self.commands[commandName]
                print("[command remove] Removed: " + commandName)

