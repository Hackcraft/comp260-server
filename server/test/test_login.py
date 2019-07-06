import unittest
import sqlite3
from server.login import Login

'''
class TestLogin(unittest.TestCase):

    def setUp(self):
        self.login = Login(None)

    def test_join(self):
        ids = [i+2 for i in range(1, 5*5)]

        self.login.join(1)
        self.login.join(5)
        self.login.join(1)



    def test_leave(self):
        pass
'''

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
