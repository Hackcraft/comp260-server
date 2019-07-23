from enum import Enum, auto

class LoginTags(Enum):

    # For client to read
    ENTER_USERNAME = auto()
    ENTER_PASSWORD = auto()
    BAD_PASSWORD = auto()

    # For server to read
    CHECK_USERNAME = auto()
    CHECK_PASSWORD = auto()
