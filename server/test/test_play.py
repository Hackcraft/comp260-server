import unittest
import sqlite3

from server import Play, Player, Vector2, DataPacket

class TestPlay(unittest.TestCase):

    @classmethod
    def setUp(cls):
        cls.player = Player()
        cls.play = Play(sqlite3.connect(':memory:'))
        cls.play.join(cls.player)
        cls.play.output_queue.get()  # Remove clear
        cls.play.output_queue.get()  # Remove welcome msg
        cls.play.output_queue.get()  # Remove room info
        cls.play.output_queue.get()  # Remove player joined room


    def test_move(self):
        last_pos = self.player.pos
        new_pos = Vector2(0, 1)
        self.play.move(self.player, new_pos)
        assert self.player.pos is new_pos

    def test_say(self):
        test_msg = 'test'
        self.play.say(self.player, test_msg)
        ply, data = self.play.output_queue.get()
        tag, msg = DataPacket.separate(data)

        assert msg == test_msg
        assert ply == self.player



