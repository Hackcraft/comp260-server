'''
	NetPacket

	A container class for the construction of net packets for
	sending and receiving. It must be read in the same order
	it was appended/written.

	It holds:
		Generic data which is added to it.
		A tag to determine what should happen.

	NetPacket: (class)
		tag (string)
		data: (queue)
			A string containing a tag for the data type, followed by the data.
			1. vec2 0 0
			2. vec2 5 5
			3. text this is a test
			etc...
'''
import json

from queue import *

from Vector2 import Vector2

class NetPacket:

	def __init__(self):
		self.data = Queue()
		self.tag = None

	# Return the vector or None
	def ReadVector(self):
		data = self.Release()
		tag = self.DataTag(data)
		if tag != Vector2.tag:
			print("Expected tag: " + Vector2.tag + ". Got: " + tag)
			return None
		else:
			return Vector2.FromString(self.StripTag(data))

	def ReadPassword(self):
		pass  # Encrypt 2x? One for main networking, again for pass

	def Release(self):
		if not self.IsEmpty():
			return self.data.get() # return and remove first element
		return None

	def IsEmpty(self):
		return self.data.qsize() < 1

	def WriteVector(self, vec2):
		self.Append("vec2 " + str(vec2))

	def WritePassword(self, passwd):
		pass

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
		jsonPacket = json.dumps(li)
		return len(jsonPacket).to_bytes(2, byteorder="little"), jsonPacket.encode()

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

	# Return the first word(tag) in a string
	def DataTag(self, string):
		return string.split(' ')[0].strip()

	# Return all but the first word(tag) in a string
	def StripTag(self, string):
		separatedStrings = string.split(' ')
		separatedStrings.pop(0)
		return ' '.join(separatedStrings)


