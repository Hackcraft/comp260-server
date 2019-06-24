class Vector2:

    def __init__(self, x, y):
        self.x = int(x)
        self.y = int(y)

    def __add__(self, other_vector2):
        if isinstance(other_vector2, Vector2):
            return Vector2(self.x + other_vector2.x, self.y + other_vector2.y)
        elif isinstance(other_vector2, int):
            return Vector2(self.x + other_vector2, self.y + other_vector2)

    def __sub__(self, other_vector2):
        if isinstance(other_vector2, Vector2):
            return Vector2(self.x - other_vector2.x, self.y - other_vector2.y)
        elif isinstance(other_vector2, int):
            return Vector2(self.x - other_vector2, self.y - other_vector2)

    def __eq__(self, other_vector2):
        if not isinstance(other_vector2, Vector2):
            return False
        return int(self.x) == int(other_vector2.x) and int(self.y) == int(other_vector2.y)

    def __ne__(self, other_vector2):
        return not (self == other_vector2)

    def __getitem__(self, index):
        if index == 0:
            return int(self.x)
        elif index == 1:
            return int(self.y)
        else:
            return None

    def __str__(self):
        return str(self.x) + " " + str(self.y)

    def __hash__(self):
        return hash((int(self.x), int(self.y)))

    def __mul__(self, other_vector2):
        if isinstance(other_vector2, Vector2):
            return Vector2(self.x * other_vector2.x, self.y * other_vector2.y)
        elif isinstance(other_vector2, int):
            return Vector2(self.x * other_vector2, self.y * other_vector2)

    @staticmethod
    def is_valid(vec2):
        return vec2 is not None and isinstance(vec2, Vector2)
