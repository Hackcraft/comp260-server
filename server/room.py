'''
    A simple data class to hold information about a room

    Not thread safe
'''
from server import Vector2

class Room:

    def __init__(self, room_id=None, name="Unknown", desc="Unknown"):
        self.room_id = room_id
        self.name = name
        self.desc = desc

        self.local_pos = Vector2(0, 0)
        self.chunk_pos = Vector2(0, 0)

        self.players = []

    def join(self, player):
        if player not in self.players:
            self.players.append(player)

    def leave(self, player):
        if player in self.players:
            self.players.remove(player)

