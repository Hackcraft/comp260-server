import sys, os
myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../')

from Hook import Hook

# NetPakcet can be created
assert Hook() != None

hook = Hook()

# Setup func to add
testVar = False
def testFunc(bool):
	global testVar
	testVar = bool
	return testVar

# Can we add a func and call it to change a var and return an output?
hook.Add("Test", "boolTest", testFunc)
output = hook.Run("Test", (True))
# Yes we can
assert testVar == True
assert output == True

# Can we remove the hook?
hook.Remove("Test", "boolTest")
hook.Run("Test", (False))
# Yes we can
assert testVar == True

# Removing one which doesn't exist won't error
hook.Remove("Test", "boolTest")

print(__file__ + " - pass")