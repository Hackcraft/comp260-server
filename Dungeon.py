from Room import Room

class Dungeon:
    CHUNK_LENGTH = 2 # for future architecture

    def __init__(self):
        self.currentRoomID = 0
        self.roomMap = {}
        self.LoadAndSetDefaultRooms()

    def LoadAndSetDefaultRooms(self):
        self.roomMap = [
            Room(1, [(0, 1), (1, 0)], "This is room 1"), # bottom left
            Room(2, [(0, 1), (-1, 0)], "This is room 2"), # bottom right
            Room(3, [(0, -1), (1, 0)], "This is room 3"), # top left
            Room(4, [(0, -1), (-1, 0)], "This is room 4") # top right
        ]

        self.currentRoomID = 0

    def CurrentRoom(self):
        return self.roomMap[self.currentRoomID];

    def MovePlayer(self, direction):
        if self.CurrentRoom().IsValidDirection(direction):
            roomIndex = self.DirectionToRoomIndex(direction)
            print(roomIndex)
            self.currentRoomID = roomIndex

    def PhraseToDirection(self, phrase):
        if phrase == "north":
            return (0, 1)
        elif phrase == "north west":
            return (-1, 1)
        elif phrase == "north east":
            return (1, 1)

        elif phrase == "south":
            return (0, -1)
        elif phrase == "south west":
            return (-1, -1)
        elif phrase == "south east":
            return (1, -1)

        elif phrase == "west":
            return (-1, 0)
        elif phrase == "east":
            return (1, 0)

    # Doesn't account for moving chunks yet
    def DirectionToRoomIndex(self, direction):
        if direction == (0, 1):
            return self.currentRoomID + self.CHUNK_LENGTH
        elif direction == (-1, 1):
            return "North West"
        elif direction == (1, 1):
            return "North East"

        elif direction == (0, -1):
            return self.currentRoomID - self.CHUNK_LENGTH
        elif direction == (-1, -1):
            return "South West"
        elif direction == (1, -1):
            return "South East"

        elif direction == (-1, 0):
            return self.currentRoomID - 1
        elif direction == (1, 0):
            return self.currentRoomID + 1