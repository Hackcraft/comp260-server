import sys, os
myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../')

from Player import Player
from Vector2 import Vector2

test_player = Player()

# Can create a player
assert test_player != None

# Their tag is player
assert test_player.GetTag() == "player"

print("Test_Player.py - pass")
