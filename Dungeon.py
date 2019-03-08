from Vector2 import Vector2
from Room import Room
from Language import Language

class Dungeon:
    CHUNK_LENGTH = 2  # for future architecture

    def __init__(self):
        self.roomMap = {}  # starts from bottom left - to far right then up
        self.LoadAndSetDefaultRooms()

    def LoadAndSetDefaultRooms(self):
        self.roomMap = [
            Room(1, [Room.EAST, Room.NORTH], "This is room 1"),  # bottom left
            Room(2, [Room.WEST, Room.NORTH], "This is room 2"),  # bottom right
            Room(3, [Room.EAST, Room.SOUTH], "This is room 3"),  # top left
            Room(4, [Room.WEST, Room.SOUTH], "This is room 4")   # top right
        ]

    def IsValidPosition(self, vec2):
        return self.PositionToRoom(vec2) != None

    def PositionToRoom(self, vec2):
        if self.PositionToRoomIndex(vec2) in self.roomMap:
            return self.roomMap[self.PositionToRoomIndex(vec2)]
        else:
            return None

    def PositionToRoomIndex(self, vec2):
        return vec2.x + (vec2.y * self.CHUNK_LENGTH)
