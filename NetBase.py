'''
    Base class for NetClient and NetServer
'''
import sys
import socket
import threading

from queue import *
from NetPacket import NetPacket

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

    def WriteVector(self, vec2):
        self.netPacket.WriteVector(self, vec2)

    def WritePassword(self, passwd):
        self.netPacket.WritePassword(self, passwd)

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

    def Receive(self, tag, func, condition = None):
        # Add to the list of receivers
        self.receiversLock.acquire()
        self.receivers[tag] = (func, condition)
        self.receiversLock.release()

    def RunReceiver(self, netPacket, clientSocket):
        self.receiversLock.acquire()
        if netPacket.GetTag() in self.receivers:
            func, condition = self.receivers[netPacket.GetTag()]
            print("Running: " + netPacket.GetTag())
            # If running on the client - not socket will be passed
            if clientSocket is None:
                func(netPacket)
            else:
                # If no condition or condition is met
                if condition is None or condition(clientSocket):
                    func(netPacket, clientSocket)
                else:
                    print("Condition not met for: " + netPacket.GetTag())
        self.receiversLock.release()



