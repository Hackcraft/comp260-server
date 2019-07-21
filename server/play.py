from server.game_state import GameState
from server.player import Player
from server.player_persistence import PlayerPersistence
from shared.vector2 import Vector2
from shared.data_tags import DataTags
from queue import Queue
import json

class Play(GameState):

    def __init__(self, db):
        super().__init__()
        self.db = db
        self.player_persistence = PlayerPersistence(db)
        self.output_queue = Queue() # (player, msg)

    def join(self, player: Player):
        super().join(player)
        self.player_persistence.load_data(player)
        self.welcome_message(player)
        self.move(player, player.pos)

    def welcome_message(self, player: Player):
        #self.output_queue
        pass

    def clear_players_screen(self, player: Player):
        self.output_queue.put((player, json.dumps({"tag": DataTags.CLEAR, "msg": "none"})))


    def leave(self, player: Player):
        super().leave(player)

    def update(self, ply: Player, msg: str):
        pass
        # Fetch the command


    def move(self, player: Player, pos: Vector2):
        pass



