class Vector2:

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other_vector2):
        return Vector2(self.x + other_vector2.x, self.y + other_vector2.y)

    def __sub__(self, other_vector2):
        return Vector2(self.x - other_vector2.x, self.y - other_vector2.y)

    def __eq__(self, other_vector2):
        if not isinstance(other_vector2, Vector2):
            return False
        return self.x == other_vector2.x and self.y == other_vector2.y

    def __ne__(self, other_vector2):
        return not (self == other_vector2)

    def __getitem__(self, index):
        if index == 0:
            return self.x
        elif index == 1:
            return self.y
        else:
            return None

    def __str__(self):
        return str(self.x) + " " + str(self.y)