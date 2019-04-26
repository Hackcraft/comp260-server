import sys, os
myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../')

from Language import Language
from Vector2 import Vector2

# Can be created
assert Language() is not None

# Can get vector from word
assert Language.WordToValue("direction", "north") == Vector2(0, 1)

# Can get word from vector
assert Language.ValueToWord("direction", Vector2(0, 1)) == "north"

# Setup a test language
Language.languages["fake"] = {
    "direction":  # Categories stay the same - words change per language
    {
        "Not North": "north",
        "Not north west": "north west",
        "Not north east": "north east",

        "Not south": "south",
        "Not south west": "south west",
        "Not south east": "south east",

        "Not west": "west",
        "Not east": "east"
    }
}

# Test language conversion
Language.ChangeLanguage("fake")
assert Language.WordToValue("direction", "Not North") == Vector2(0, 1)
assert Language.ValueToWord("direction", Vector2(0, 1)) == "Not North"

print(__file__ + " - pass")


