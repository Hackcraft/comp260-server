'''
    Base class for NetClient and NetServer
'''
import sys
import socket
import threading

from queue import *
from NetPacket import NetPacket
from Hook import Hook

class NetBase:
    PACKET_ID = "HMUD"

    # References to all instances created
    instancesLock = threading.Lock()
    netInstances = [] # All instances of NetBase and derivatives

    # Incomming
    incommingQueue = Queue()

    # Receivers
    receiversLock = threading.Lock()
    receivers = {} # tag : func

    def __init__(self):
        self.netPacket = NetPacket()
        # Add this instance to the global list
        self.instancesLock.acquire()
        self.netInstances.append(self)
        self.instancesLock.release()

    def __del__(self):
        self.Remove()

    def Remove(self):
        # Remove this instance from the global list
        self.instancesLock.acquire()
        try:
            self.netInstances.remove(self)
        except:
            pass
        self.instancesLock.release()

    def Start(self, tag = None):
        self.netPacket = NetPacket()
        self.netPacket.SetTag(tag)

    def Write(self, string):
        self.netPacket.Append(string)

    def Send(self, targetSocket):
        try:
            targetSocket.send(self.PACKET_ID.encode())

            # Get the data size and encoded data
            size, data = self.netPacket.Encode()

            # Send data size
            targetSocket.send(size)

            # Send data encoded
            targetSocket.send(data)
            print("Sending: " + self.netPacket.GetTag())
        except socket.error:
            print("Failed to send data!")

    def Receive(self, tag, func):
        # Add to the list of receivers
        self.receiversLock.acquire()
        self.receivers[tag] = func # args(NetPacket, ClientSocket or None)
        self.receiversLock.release()

    def RunReceiver(self, netPacket, clientSocket):
        self.receiversLock.acquire()
        if netPacket.GetTag() in self.receivers:
            print("Running: " + netPacket.GetTag())
            # If running on the client - not socket will be passed
            if clientSocket is None:
                self.receivers[netPacket.GetTag()](netPacket)
            else:
                self.receivers[netPacket.GetTag()](netPacket, clientSocket)
        self.receiversLock.release()



