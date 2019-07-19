import unittest

from client.ui import UI

# Literally just input and output queues - for writing to the screen and reading input
# No real logic to test

class TestUI(unittest.TestCase):

    @classmethod
    def setUp(cls):
        cls.ui = UI()