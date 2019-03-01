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
assert netPacket.Encode() == '["Test", "First data", "Second data"]'.encode()

# Check decoding works
netPacket.DecodeAndLoad(netPacket.Encode())
assert netPacket.GetTag() == "Test"
assert netPacket.Release() == "First data"
assert netPacket.Release() == "Second data"

print("Test_NetPacket.py - pass")
