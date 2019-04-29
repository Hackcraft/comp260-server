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
    MAX_PROCESSING_AT_ONCE = 100

    # Reference to whether the net is the client (NetClient)
    localPlayer = False

    # References to all instances created
    instancesLock = threading.RLock()
    netInstances = [] # All instances of NetBase and derivatives

    # Multithreading queues (player, netPacket)
    inputQueue = Queue()

    # Receivers
    receiversLock = threading.RLock()
    receivers = {} # tag : func
    removed = []

    hasConnection = False

    def __init__(self):
        self.netPacket = NetPacket()
        # Add this instance to the global list
        with self.instancesLock:
            self.netInstances.append(self)

    def __del__(self):
        self.Remove()

    def Remove(self):
        # Remove this instance from the global list
        with self.instancesLock:
            try:
                self.netInstances.remove(self)
            except:
                pass

    def Start(self, tag = None):
        self.netPacket = NetPacket()
        self.netPacket.SetTag(tag)

    def Write(self, type, data = None):
        self.netPacket.Write(type, data)

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
        with self.receiversLock:
            if tag in self.removed:
                return

            print("Got past lock")
            print(tag, func, condition)
            try:
                self.receivers[tag] = (func, condition)
            except Exception as error:
                print(error)
            print(tag, func, condition)
        print(tag, func, condition)

    def RemoveReceive(self, tag):
        with self.receiversLock:
            if tag in self.receivers and tag not in self.removed:
                self.removed.append(tag)

    def RunReceiver(self, netPacket, clientSocket):
        with self.receiversLock:

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

            elif netPacket.GetTag() != netPacket.invalidPacketTag:
                print("No receivers found for: " + netPacket.GetTag())


    def Update(self):
        self.ProcessInput()

    def ProcessInput(self):
        count = 0

        while(self.inputQueue.qsize() > 0 and count < self.MAX_PROCESSING_AT_ONCE):
            input = self.inputQueue.get()
            player = input[0]
            netPakcet = input[1]

            self.RunReceiver(netPakcet, player)

            count += 1



