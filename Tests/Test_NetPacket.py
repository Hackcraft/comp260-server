import sys, os
myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../')

from NetPacket import NetPacket

# NetPakcet can be created
assert NetPacket() != None

# Check encoding works
netPacket = NetPacket()
netPacket.SetTag("Test")
netPacket.Append("First data")
netPacket.Append("Second data")

# Check decoding works
#netPacket.DecodeAndLoad(netPacket.Encode())
assert netPacket.GetTag() == "Test"
assert netPacket.Release() == "First data"
assert netPacket.Release() == "Second data"

# NetType fancy checks -- Vector2
from Vector2 import Vector2

originalVec2 = Vector2(100, 100)
typePacket = NetPacket()
typePacket.Write(Vector2, originalVec2)
newVec2 = typePacket.Read(Vector2)

assert originalVec2 == newVec2

# NetType fancy checks -- GameState
from GameState import GameState

originalGS = GameState.LOGIN
typePacket = NetPacket()
typePacket.Write(GameState, originalGS)
newGS = typePacket.Read(GameState)

print(originalGS)
print(newGS)

assert originalGS == newGS




print(__file__ + " - pass")
