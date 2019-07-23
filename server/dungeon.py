import math

from server import Room, Vector2

'''
    A map class of rooms
    
    
'''

class Dungeon:
    CHUNK_LENGTH = 2  # for future architecture

    NORTH = Vector2(0, 1)
    EAST = Vector2(1, 0)
    SOUTH = Vector2(0, -1)
    WEST = Vector2(-1, 0)

    NAME_TO_DIRECTION = {
        "north": NORTH,
        "east": EAST,
        "south": SOUTH,
        "west": WEST
    }

    def __init__(self, db):
        self.db = db
        self._rooms = {}  # x,y: Room

        self._load()

    def _load(self):
        self._rooms = [
            Room(1, [self.EAST, self.NORTH], "This is room 1"),  # bottom left
            Room(2, [self.WEST, self.NORTH], "This is room 2"),  # bottom right
            Room(3, [self.EAST, self.SOUTH], "This is room 3"),  # top left
            Room(4, [self.WEST, self.SOUTH], "This is room 4")  # top right
        ]

        self.assign_positions_to_rooms()

    def assign_positions_to_rooms(self):
        for i in range(0, len(self._rooms)):
            self._rooms[i].local_pos = self.position_at_room_index(i)

    def is_valid_position(self, vec2: Vector2):
        return self.room_at_position(vec2) is not None

    def room_at_position(self, vec2: Vector2):
        index = self.room_index_at_position(vec2)
        if 0 <= index < len(self._rooms) and self._rooms[index] is not None:
            return self._rooms[index]
        else:
            return None

    def room_index_at_position(self, vec2: Vector2):
        return int(vec2.x + (vec2.y * self.CHUNK_LENGTH))

    def position_at_room_index(self, index: int):
        max_index = self.CHUNK_LENGTH * self.CHUNK_LENGTH - 1
        vec2 = Vector2(0, 0)
        vec2.x = int(index % self.CHUNK_LENGTH)
        vec2.y = int(math.floor(min(max_index, index) / self.CHUNK_LENGTH))
        return vec2

    #def global_position_of_room(self, room: Room):
    #    return room.local_pos + (room.chunk_pos * self.CHUNK_LENGTH)

    def directions_from_room(self, room):
        directions = []
        if self.room_at_position(room.local_pos + self.NORTH):
            directions.append("north")
        if self.room_at_position(room.local_pos + self.EAST):
            directions.append("east")
        if self.room_at_position(room.local_pos + self.SOUTH):
            directions.append("south")
        if self.room_at_position(room.local_pos + self.WEST):
            directions.append("west")
        return ', '.join(directions)

    def save(self):
        raise NotImplementedError




