from Data_Handlers.Database import Database

db = Database()

class PlayerData:

    def __init__(self):
        # Create tables
        pass

    def UpdatePosition(self):
        # player.chunkX = 0
        # player.chunkY = 0
        # player.room = 0
        pass

    def SetCredentials(self, username, password):
        # Save username
        # Save hashed password
        pass

    # Use await and async to return?
    def CheckCredentials(self, username, password):
        # Look in mysql for details