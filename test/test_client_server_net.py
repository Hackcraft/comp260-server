import unittest
from client.net_connection import NetConnection as CLConnection
from server.net_connection import NetConnection as SVConnection

class TestClientServerConnection(unittest.TestCase):


    def setUp(self):
        self.IP = "127.0.0.1"
        self.PORT = 8222

        self.sv = SVConnection(self.IP, self.PORT)
        self.cl = CLConnection(self.IP, self.PORT)


    def tearDown(self):
        self.cl.close()
        self.sv.close()

    def test_connection(self):
        pass


