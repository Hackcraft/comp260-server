import unittest
import random
from game_state import GameState

class TestGameState(unittest.TestCase):

    @classmethod
    def setUp(self):
        self.game_state = GameState()
        self.player_id = random.randrange(255)

    # Single join/leave
    def test_single_join(self):
        self.game_state.join(self.player_id)
        assert self.game_state.contains_player(self.player_id)

    def test_single_leave(self):
        self.game_state.join(self.player_id)
        self.game_state.leave(self.player_id)
        assert not self.game_state.contains_player(self.player_id)

    # Duplicate join/leave
    def test_duplicate_join(self):
        self.game_state.join(self.player_id)
        self.game_state.join(self.player_id)
        assert self.game_state.contains_player(self.player_id)

    def test_duplicate_leave(self):
        self.game_state.join(self.player_id)
        self.game_state.join(self.player_id)
        self.game_state.leave(self.player_id)
        assert not self.game_state.contains_player(self.player_id)

    # Multiple join/leave
    def test_multiple_join(self):
        for i in range(0, 20):
            self.game_state.join(i)

        for i in range(0, 20):
            assert self.game_state.contains_player(i)

    def test_multiple_leave(self):
        for i in range(0, 20):
            self.game_state.join(i)

        for i in range(0, 20):
            self.game_state.leave(i)

        for i in range(0, 20):
            assert not self.game_state.contains_player(i)