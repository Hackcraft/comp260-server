import sys, os
myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../')

from Entity import Entity
from Vector2 import Vector2

# Entities can be created
assert Entity() != None

# Create test Entities
test_ent1 = Entity()
test_ent2 = Entity()

# Entity tags can be read
assert test_ent1.tag != None
assert test_ent2.tag != None

# Entity pos can be read
assert test_ent1.pos != None
assert test_ent2.pos != None

test_ent1.tag = "TestTag"
test_ent1.id = 666
test_ent1.pos = Vector2(6, 6)

# Entities can be printed
assert str(test_ent1) == "TestTag" + ": " + str(666) + " at " + str(Vector2(6, 6))

print("Test_Entity.py - pass")
