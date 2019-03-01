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

# Entity tags can be set and get
test_tag = 1
test_ent1.SetTag(test_tag)
assert test_ent1.GetTag() == test_tag

# Entity pos can be set and get with vec2
test_pos = Vector2(5, 5)
test_ent1.SetPos(test_pos)
assert test_ent1.GetPos() == test_pos
assert test_ent1.GetX() == test_pos.x
assert test_ent1.GetY() == test_pos.y

# Entity can be moved with vec2
test_moveBy = Vector2(1, 1)
test_moveExpec = test_pos + Vector2(1, 1)
test_ent1.Move(test_moveBy)
assert test_ent1.GetPos() == test_moveExpec

# Entity ID can be set and get
test_ID = 5
test_ent1.SetID(test_ID)
assert test_ent1.GetID() == test_ID

# Entities can be printed
assert str(test_ent1) == str(test_tag) + ": " + str(test_ID) + " at " + str(test_moveExpec)

print("Test_Entity.py - pass")
