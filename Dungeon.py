import math

from Vector2 import Vector2
from Room import Room
from Language import Language

class Dungeon:
    CHUNK_LENGTH = 2  # for future architecture

    def __init__(self):
        self.roomMap = {}  # starts from bottom left - to far right then up
        self.LoadAndSetDefaultRooms()
        self.AssignRoomPositions()

    def LoadAndSetDefaultRooms(self):
        self.roomMap = [
            Room(1, [Room.EAST, Room.NORTH], "This is room 1"),  # bottom left
            Room(2, [Room.WEST, Room.NORTH], "This is room 2"),  # bottom right
            Room(3, [Room.EAST, Room.SOUTH], "This is room 3"),  # top left
            Room(4, [Room.WEST, Room.SOUTH], "This is room 4")   # top right
        ]

    def AssignRoomPositions(self):
        for i in range(0, len(self.roomMap)):
            self.roomMap[i].localPos = self.RoomIndexToPosition(i)

    def IsValidPosition(self, vec2):
        return self.PositionToRoom(vec2) != None

    def PositionToRoom(self, vec2):
        index = self.PositionToRoomIndex(vec2)
        if 0 <= index < len(self.roomMap) and self.roomMap[index] is not None:
            return self.roomMap[self.PositionToRoomIndex(vec2)]
        else:
            return None

    def PositionToRoomIndex(self, vec2):
        return int(vec2.x + (vec2.y * self.CHUNK_LENGTH))

    def RoomIndexToPosition(self, index):
        maxIndex = self.CHUNK_LENGTH * self.CHUNK_LENGTH - 1
        vec2 = Vector2(0, 0)
        vec2.x = int(index % self.CHUNK_LENGTH)
        vec2.y = int(math.floor(min(maxIndex, index) / self.CHUNK_LENGTH))
        return vec2

    def GlobalPositionFromRoom(self, room):
        return room.localPos + (room.chunkPos * self.CHUNK_LENGTH)

#    def GlobalPositionToRoom(self, vec2):
#        return
