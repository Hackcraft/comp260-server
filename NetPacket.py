'''
	NetPacket

	A container class for the construction of net packets for
	sending and receiving. It must be read in the same order
	it was appended.

	It holds:
		Generic data which is added to it.
		A tag to determine what should happen.
'''
import json

from queue import *

class NetPacket:

	def __init__(self):
		self.data = Queue()
		self.tag = None

	# Data
	def Release(self):
		if not self.IsEmpty():
			return self.data.get() # return and remove first element
		return None

	def IsEmpty(self):
		return self.data.qsize() < 1

	def Append(self, data):
		self.data.put(data)

	# Tag
	def HasTag(self):
		return self.GetTag() != None

	def GetTag(self):
		return self.tag

	def SetTag(self, tag):
		self.tag = tag

	# Validity
	def IsValid(self):
		return self.HasTag()

	# Encodings
	def Encode(self):
		# Queue -> tag + List -> JSON -> encode
		li = [self.tag] + list(self.data.queue)
		return json.dumps(li).encode()

	def DecodeAndLoad(self, data):
		decoded = self.Decode(data)
		self.tag = decoded[0]
		self.data = decoded[1]

	def Decode(self, data):
		# returns (tag, dataQueue)
		decode = data.decode("utf-8")
		arr = json.loads(decode)
		tag = arr[0]
		queue = Queue()
		for i in range(1, len(arr)):
			queue.put(arr[i])
		return (tag, queue)

	def __str__(self):
		# Queue -> List -> tag + List
		li = list(self.data.queue)
		output = str(self.tag) + "\n" + str(li)[1:-1]
		return output


