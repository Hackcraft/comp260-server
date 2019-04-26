from NetType import NetType

class Vector2(NetType):
    tag = "vec2"

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

    @classmethod
    def ToNetString(cls, vec2):
        return Vector2.tag + " " + str(vec2)

    @classmethod
    def FromNetString(cls, string):
        # Extract the tag
        tag = cls.DataTag(string)
        # Validate the tag
        if tag != Vector2.tag:
            print("Expected tag: " + Vector2.tag + ". Got: " + tag)
            return None
        # Remove the tag
        data = cls.StripTag(string)
        # Create a vector from the data
        split = data.split(' ')
        if len(split) <= 2:
            x = split[0].strip()
            y = split[1].strip()
            if int(x) != x or int(y) != y:
                return Vector2(x, y)
            else:
                print("Expected two numbers to create Vector2, x or y is not a number.")
                return None
        else:
            print("Expected two numbers to create Vector2, x and y.")
            return None

    @staticmethod
    def IsValid(vec2):
        return vec2 is not None and isinstance(vec2, Vector2)
