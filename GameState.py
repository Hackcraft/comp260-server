from NetType import NetType

class GameState(NetType):
    tag = "gs"

    # Enum type system (enum import was causing problems)
    LOGIN = 0
    PLAY = 1

    states = [
        "LOGIN",
        "PLAY"
    ]

    @classmethod
    def PositionOfState(cls, state):
        index = None
        try:
            index = cls.states.index(state)
        except:
            pass
        print(cls.states.index("LOGIN"))
        return index

    @classmethod
    def StateFromPosition(cls, pos):
        if pos in cls.states:
            return cls.states[pos]
        else:
            return None

    @classmethod
    def ToNetString(cls, gameState):
        return cls.tag + " " + str(gameState)  # gameState will be passed as an int

    @classmethod
    def FromNetString(cls, string):
        # Extract the tag
        tag = cls.DataTag(string)
        # Validate the tag
        if tag != GameState.tag:
            print("Expected tag: " + GameState.tag + ". Got: " + tag)
            return None
        # Remove the tag
        data = cls.StripTag(string)
        # Create a GameState from the data
        gameState = None
        try:
            num = int(data)
            if num < len(cls.states) and num >= 0:
                gameState = num
        except Exception as error:
            print(error)

        return gameState



