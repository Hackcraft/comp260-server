from server import GameState, Player, PlayerPersistence, Dungeon, Vector2, DataTags

from queue import Queue
import json

class Play(GameState):

    def __init__(self, db):
        super().__init__()
        self.db = db
        self.player_persistence = PlayerPersistence(db)
        self.dungeon = Dungeon(db)
        self.output_queue = Queue() # (player, msg)

    def join(self, player: Player):
        super().join(player)
        self.player_persistence.load_data(player)
        self.clear_players_screen(player)
        self.welcome_message(player)
        self.move(player, player.pos)

    def send(self, player, tag, msg="none"):
        self.output_queue.put((player, json.dumps({"tag": tag, "msg": msg})))

    def welcome_message(self, player: Player):
        msg = "Welcome to the Dungeon!"
        self.send(player, DataTags.WRITE, msg)

    def clear_players_screen(self, player: Player):
        self.send(player, DataTags.CLEAR)


    def leave(self, player: Player):
        super().leave(player)

    def update(self, ply: Player, msg: str):
        raise NotImplementedError
        # Fetch the command


    def move(self, player: Player, pos: Vector2):
        pass

    # Save the current game state
    def save(self):
        raise NotImplementedError
        # Save player data
        for player in self.players:
            self.player_persistence.save_data(player)

        # Save room data
        pass



