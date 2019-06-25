from login import Login

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
