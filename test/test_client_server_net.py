import unittest
import time
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
        pass

    def test_connection(self):
        print("Testing")

        time.sleep(.5)

        self.cl.send("This is a test")
        self.cl.send("This is second test")
        self.cl.send("This is third test")

        tmp_clients = []
        tmp_count = 5

        for i in range(tmp_count):
            tmp_clients.append(CLConnection(self.IP, self.PORT))

        time.sleep(1)

        for client in tmp_clients:
            client.send("This is a test")

        time.sleep(1)

        server_clients = list(self.sv.connects.queue)

        for client_id in server_clients:
            self.sv.send(client_id, "Hello client %d " % client_id)

        time.sleep(1)

        for client in tmp_clients:
            while client.incoming_queue.qsize() > 0:
                print("Server wrote: %s" % client.incoming_queue.get())

        while self.sv.message_queue.qsize() > 0:
            (client_id, message) = self.sv.message_queue.get()
            print("Client: %d wrote: %s" % (client_id, message))

        time.sleep(1)

        print("Stopped testing")




