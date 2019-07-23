from enum import Enum, auto

class DataTags(Enum):

    # Client actions
    CLEAR = auto()  # Clear the screen of the client
    WRITE = auto()  # Write a message to the screen of the client

    # Client msg processing is all done server side so the client will
    # send direct output from their game with no processing

#print(DataTags.CLEAR.__class__.__name__)
#print(DataTags(3).name)
