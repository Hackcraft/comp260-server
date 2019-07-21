import threading
from server.player import Player

class GameState:

    def __init__(self):
        self.players_lock = threading.Lock()
        self.players = {}

    def join(self, player: Player):
        if isinstance(player, Player):
            with self.players_lock:
                if player not in self.players:
                    self.players[player] = player

    def leave(self, player: Player):
        if isinstance(player, Player):
            with self.players_lock:
                if player in self.players:
                    del self.players[player]

    def contains_player(self, player: Player):
        with self.players_lock:
            if player in self.players:
                return True
            return False

    def update(self, player_id, message):
        pass
