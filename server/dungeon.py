import math

from server import Room, Vector2, RoomPersistence

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
        self.room_persistence = RoomPersistence(db)
        self._rooms = {}  # id: Room

        self._load()

    def _load(self):
        self._rooms = [
            Room(1, "This is room 1", "This is no ordinary room."),  # bottom left
            Room(2, "This is room 2", "This is an ordinary room."),  # bottom right
            Room(3, "This is room 3", "This is no ordinary room."),  # top left
            Room(4, "This is room 4", "This is an ordinary room.")  # top right
        ]

        self._assign_positions_to_rooms()
        self._load_room_data()

    def _assign_positions_to_rooms(self):
        for i in range(0, len(self._rooms)):
            self._rooms[i].local_pos = self.position_at_room_index(i)

    def _load_room_data(self):
        for room in self._rooms:
            self.room_persistence.load_data(room)

    def is_valid_position(self, vec2: Vector2):
        return self.room_at_position(vec2) is not None

    def room_at_position(self, vec2: Vector2):
        index = self.room_index_at_position(vec2)
        if 0 <= vec2.x < self.CHUNK_LENGTH > vec2.y >= 0 and \
            0 <= index < len(self._rooms) and self._rooms[index] is not None:
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

    # Commented out because the current setup for 'directions_from_room' doesn't support chunks - also working on MVP
    #def global_position_of_room(self, room: Room):
    #    return room.local_pos + (room.chunk_pos * self.CHUNK_LENGTH)

    def directions_from_room(self, room):
        directions = [name for name in self.NAME_TO_DIRECTION
                      if self.room_at_position(room.local_pos + self.NAME_TO_DIRECTION[name])]
        return ', '.join(directions)

    def save(self):
        for room in self._rooms:
            self.room_persistence.save_data(room)




