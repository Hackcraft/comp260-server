'''
    id (int)
        range(0-chunkSize * 0-chunkSize)

    connections (array)
        0   direction (x, y)
        1   direction (x, y)

    description (string)
        ^^

    Support Language in future
'''


class Room:
    def __init__(self, id, connections, description):
        self.id = id
        self.connections = connections
        self.description = description

    def Description(self):
        return self.description

    def IsValidDirection(self, directionToFind):
        isValid = False

        for direction in self.connections:
            if direction == directionToFind:
                isValid = True
                break

        return isValid

    def DirectionsParser(self):
        directions = ""

        for direction in self.connections:
            directions += self.DirectionParser(direction) + " | "

        return directions

    def DirectionParser(self, direction):
        # x, y
        if direction == (0, 1):
            return "North"
        elif direction == (-1, 1):
            return "North West"
        elif direction == (1, 1):
            return "North East"

        elif direction == (0, -1):
            return "South"
        elif direction == (-1, -1):
            return "South West"
        elif direction == (1, -1):
            return "South East"

        elif direction == (-1, 0):
            return "West"
        elif direction == (1, 0):
            return "East"
