from server import Vector2

class Player:

    def __init__(self, player_id = None, pos = Vector2(0, 0)):
        self.player_id = player_id
        self._pos = Vector2.copy(pos)

        self.username = None
        self.nickname = None

        self.connection_id = None
        self.salt = None
        self.login_verified = False

    @property
    def pos(self):
        return Vector2.copy(self._pos)

    @pos.setter
    def pos(self, vec2: Vector2):
        self._pos = Vector2.copy(vec2)

    def get_name(self):
        return self.nickname or self.username

    def get_true_name(self):
        if self.nickname is not None and self.nickname != self.username:
            return '%s (%s)' % (self.nickname, self.username)
        else:
            return self.get_name()

    def is_connected(self):
        return self.connection_id is not None

    def is_valid(self):
        return self.is_connected() and self.login_verified

    def __key(self):
        return self.player_id

    def __eq__(self, other):
        if isinstance(other, Player):
            return self.__key() == other.__key()
        return NotImplemented

    def __hash__(self):
        return hash(self.__key())
