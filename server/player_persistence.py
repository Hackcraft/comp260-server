import sqlite3
from server import Player

class PlayerPersistence:

    def __init__(self, db):
        self.db = db
        self.cursor = db.cursor()

        self._set_up_table()

    def _set_up_table(self):
        raise NotImplementedError

    def load_data(self, player: Player):
        return player  # TODO IMPLEMENT

    def save_data(self, player: Player):
        pass  # TODO IMPLEMENT
