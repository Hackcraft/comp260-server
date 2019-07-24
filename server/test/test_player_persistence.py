import unittest
import sqlite3

from server import PlayerPersistence, Player, Vector2

class TestPlayerPersistence(unittest.TestCase):

    @classmethod
    def setUp(cls):
        cls.pp = PlayerPersistence(sqlite3.connect(':memory:'))
        cls.player = Player()
        cls.player.player_id = 1
        cls.player.username = 'bob'

    def test_save_load_pos(self):
        self.player.pos = Vector2(0, 1)
        self.pp.save_data(self.player)

        self.player.pos = Vector2(0, 0)
        self.pp.load_data(self.player)

        assert self.player.pos == Vector2(0, 1)

    def test_save_load_nick(self):
        self.player.nickname = 'new_name'
        self.pp.save_data(self.player)

        self.player.nickname = None
        self.pp.load_data(self.player)

        assert self.player.get_name() == 'new_name'
