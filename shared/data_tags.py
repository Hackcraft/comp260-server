from enum import Enum, auto

class DataTags(Enum):

    # Client actions
    CLEAR = auto()  # Clear the screen of the client
    WRITE = auto()  # Write a message to the screen of the client

    # Server actions
    MOVE = auto()   # Move the player to a new position
    LOCAL_CHAT = auto()  # Write a message to everyone in the current room



print(DataTags(3).name)
