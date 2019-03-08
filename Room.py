'''
    id (int)
        range(0-chunkSize * 0-chunkSize)

    connections (array)
        0   direction (x, y)
        1   direction (x, y)

    description (string)
        ^^

    Support Language in future
'''
import threading

from Vector2 import Vector2
from Language import Language

class Room:

    NORTH = Language.BaseWordToValue("direction", "north")
    EAST = Language.BaseWordToValue("direction", "east")
    SOUTH = Language.BaseWordToValue("direction", "south")
    WEST = Language.BaseWordToValue("direction", "west")

    NORTH_EAST = Language.BaseWordToValue("direction", "north east")
    NORTH_WEST = Language.BaseWordToValue("direction", "north west")

    SOUTH_EAST = Language.BaseWordToValue("direction", "south east")
    SOUTH_WEST = Language.BaseWordToValue("direction", "south west")

    def __init__(self, id, connections, description):
        self.id = id
        self.connections = connections
        self.description = description

        self.players = []
        self.playersLock = threading.Lock()

