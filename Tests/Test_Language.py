import sys, os
myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../')

from Language import Language
from Vector2 import Vector2

# Can be created
assert Language() != None

language = Language()

# Can get vector from word
assert language.WordToValue("north") == Vector2(0, 1)

# Can get word from vector
assert language.ValueToWord(Vector2(0, 1)) == "north"

print("Test_Language.py - pass")


