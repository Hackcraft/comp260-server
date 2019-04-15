import sys, os
myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../')

from Command import Command

command = Command()
calledBacked = False
argStr = "test first second third"

def CallBack(player, command, args, argsStr):
    global calledBacked
    calledBacked = True
    print(args)
    assert len(args) == 3  # first, second, third


command.Add("test", CallBack)
command.Run(None, "test", argStr)

assert calledBacked is True

print(__file__ + " - pass")
