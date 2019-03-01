'''
	Base class for NetClient and NetServer
'''
import sys
import socket
import threading

from queue import *
from NetPacket import NetPacket

class NetBase:

	# References to all instances created
	instancesLock = threading.Lock()
	netInstances = []

	# Incomming
	incommingQueue = Queue()

	def __init__(self):
		self.netPacket = NetPacket()
		# Add this instance to the global list
		self.instancesLock.acquire()
		self.netInstances.append(self)
		self.instancesLock.release()

	def __del__(self):
		# Remove this instance from the global list
		self.instancesLock.acquire()
		self.netInstances.remove(self)
		self.instancesLock.release()

	def Start(self, tag = None):
		self.netPacket.SetTag(tag)

	def Send(self, targetSocket):
		try:
			targetSocket.send(netPacket.encode())
		except socket.error:


