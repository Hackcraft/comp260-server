'''
    Handles room creation and perm updating:
        When a player is added or removed to a room - map tells the room and updates the db
        Room will contain copies of online players only
        The database will treat offline and online players as the same
        Rooms will be created empty


'''

import sqlite3

from server.room import Room

class Map:

    def __init__(self, room_database):
        self.database = room_database
        self.cursor = room_database.cursor()
        self.rooms = {}  # ['x, y'] = Room

    def _load_rooms(self):
        self.cursor.execute('select * from rooms')
        rows = self.cursor.fetchall()

    # Don't forget the player will save the room to itself
    def move_to_room(self, player_id, x, y):
        room = self._get_room(x, y)
        if room is not None:
            room.join(player_id)
            self.cursor.execute('')

    def _get_room(self, x, y):
        key = str(x) + ', ' + str(y)
        if key in self.rooms:
            return self.rooms[key]
        return None
