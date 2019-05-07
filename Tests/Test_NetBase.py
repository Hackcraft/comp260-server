import sys, os
myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../')

from NetBase import NetBase

# NetPakcet can be created
netInstance = NetBase()
assert netInstance != None

# NetPacket can be removed from internal list
netInstance.Remove()
assert len(netInstance.netInstances) == 0

netBase1 = NetBase()
netBase2 = NetBase()

# Two instances can be referenced
assert len(netBase1.netInstances) == 2

# Can add receivers
netBase1.Receive("netBase1", print)
netBase2.Receive("netBase2", print)

# Receivers are in
assert len(netBase1.receivers) == 2
assert netBase1.receivers["netBase2"][0] == print  # Stored in tuple
assert netBase2.receivers["netBase1"][0] == print



print(__file__ + " - pass")

