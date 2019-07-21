class Room:

    def __init__(self, obj_id=None, name="Unknown", desc="Unknown", dirs=[]):
        self.obj_id = obj_id
        self.name = name
        self.desc = desc
        self.dirs = dirs
        self.players = []

    def join(self, player):
        if player not in self.players:
            self.players.append(player)

    def leave(self, player):
        if player in self.players:
            self.players.remove(player)

