class Room:

    def __init__(self, obj_id=None, name="Unknown", desc="Unknown", dirs=[]):
        self.obj_id = id
        self.name = name
        self.desc = desc
        self.dirs = dirs
        self.players = []

    def join(self, player_id):
        if player_id not in self.players:
            self.players.append(player_id)

    def leave(self, player_id):
        if player_id in self.players:
            self.players.remove(player_id)

