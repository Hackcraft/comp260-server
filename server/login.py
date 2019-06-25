from game_state import GameState
import threading

class Login(GameState):

    def __init__(self, db):
        super().__init__()
        self.db = db

        self.verified = []
        self.verified_lock = threading.Lock()

        self.user_names = []
        self.user_names_lock = threading.Lock()

    def join(self, player_id):
        super().join(player_id)

    def leave(self, player_id):
        super().leave(player_id)
        # Remove from verified
        with self.verified_lock:
            if player_id in self.verified:
                self.verified.remove(player_id)
        # Remove selected username
        with self.user_names_lock:
            if player_id in self.user_names:
                del self.user_names[player_id]

    def is_verified(self, player_id):
        with self.verified_lock:
            return player_id in self.verified

    def selected_username(self, player_id):
        with self.user_names_lock:
            if player_id in self.user_names:
                return self.user_names[player_id]

    def update(self, player_id, message):



