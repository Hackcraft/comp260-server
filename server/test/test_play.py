import unittest
import sqlite3

from server import Play, Player, Vector2

class TestPlay(unittest.TestCase):

    @classmethod
    def setUp(cls):
        cls.player = Player()
        cls.play = Play(sqlite3.connect(':memory:'))
        cls.play.join(cls.player)


    def test_move(self):
        last_pos = self.player.pos
        new_pos = Vector2(0, 1)
        self.play.move(self.player, new_pos)
        assert self.player.pos is new_pos


