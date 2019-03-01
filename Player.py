from Entity import Entity

class Player(Entity):

    def __init__(self):
        super().__init__()
        self.SetTag("player")