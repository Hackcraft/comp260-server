import unittest
import sqlite3

from server import Login, Player

class TestLoginDatabase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        print("help")
        cls.username = "Test_username"
        cls.salt = Login.generate_salt()
        cls.salted_password = Login.salt_password(cls.salt, "password")

    def setUp(self):
        self.database = sqlite3.connect(':memory:')
        self.login = Login(self.database)

        self.login.create_account(self.username, self.salted_password, self.salt)

    def test_account_creation(self):
        assert self.login.username_exists(self.username)

    def test_password(self):
        assert self.login.password_correct(self.username, self.salted_password)

    def test_fetch_salt(self):
        assert self.login.user_salt(self.username) == self.salt

    def test_update_to_login(self):
        player = Player(1)
        player_name = "TestMe"
        self.login.join(player)

        # First is username
        self.login.update(player, player_name)

        # Second is password - no account TestMe so will create new
        self.login.update(player, self.salted_password)

        # Verify the user was created
        assert self.login.user_salt(player_name) is not None
        assert self.login.username_exists(player_name)

        # Verify the user is verified
        assert player.login_verified