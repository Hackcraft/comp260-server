import threading

class GameState:

    def __init__(self):
        self.players_lock = threading.Lock()
        self.players = []

    def join(self, player_id):
        with self.players:
            if player_id not in self.players:
                self.players[player_id] = True

    def leave(self, player_id):
        with self.players:
            if player_id in self.players:
                del self.players[player_id]

    def contains_player(self, player_id):
        with self.players:
            if player_id in self.players:
                return True
            return False

    def update(self, player_id, message):
        pass
