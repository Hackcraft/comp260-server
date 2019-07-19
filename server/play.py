from server.game_state import GameState

class Play(GameState):

    def __init__(self, db):
        super().__init__()
        self.db = db

    def update(self, player_id, message):


