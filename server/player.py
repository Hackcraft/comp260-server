from game_state import GameState
from room import Room
from queue import Queue

class Player:

    def __init__(self, player_id, game_state, room):
        self.player_id = player_id
        self._game_state = game_state
        self._room = room

    @property
    def game_state(self):
        return self._game_state

    @game_state.setter
    def game_state(self, game_state):
        if not isinstance(GameState, game_state):
            raise ValueError("Given invalid game_state")

        if self._game_state is not None:
            self._game_state.leave(self.player_id)

        self._game_state = game_state
        self._game_state.enter(self.player_id)

    @property
    def room(self):
        return self._room

    @room.setter
    def room(self, room):
        if not isinstance(Room, room):
            raise ValueError("Given invalid room")

        if self._room is not None:
            self._room.leave(self.player_id)

        self._room = room
        self._room.enter(self.player_id)

    def __del__(self):
        if self._game_state is not None:
            self._game_state.leave(self.player_id)

        if self._room is not None:
            self._room.leave(self.player_id)