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

	# References to all instances created
	instancesLock = threading.Lock()
	netInstances = [] # All instances of NetBase and derivatives

	# Incomming
	incommingQueue = Queue()

	# Receivers
	receiversLock = threading.Lock()
	receivers = {} # tag : func

	# Hooks
	hook = Hook()

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
		self.netPacket.SetTag(tag)

	def Write(self, string):
		self.netPacket.Append(string)

	def Send(self, targetSocket):
		raise NotImplementedError()

	def Receive(self, tag, func):
		# Add to the list of receivers
		self.receiversLock.acquire()
		self.receivers[tag] = func # args(NetPacket, ClientSocket or None)
		self.receiversLock.release()

	def RunReceiver(self, netPacket, clientSocket = None):
		self.receiversLock.acquire()
		if netPacket.GetTag() in self.receivers:
			self.receivers[netPacket.GetTag()](netPacket, clientSocket)
		self.receiversLock.release()




