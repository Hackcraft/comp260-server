import unittest
import sqlite3

from server import Dungeon, Room


class TestDungeon(unittest.TestCase):

    @classmethod
    def setUp(cls):
        cls.dungeon = Dungeon(sqlite3.connect(':memory:'))
        cls.room = Room()

    def test_directions_parser(self):
        assert self.dungeon.directions_from_room(self.room) == 'north, east'
