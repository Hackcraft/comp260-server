from Vector2 import Vector2

class Entity():

	def __init__(self):
		self.pos = Vector2(0, 0)
		self.tag = "unassigned"
		self.ID = 0

	def SetPos(self, vec2):
			self.pos = vec2

	def GetPos(self):
		return self.pos

	def Move(self, vec2):
		self.pos = self.pos + vec2

	def GetX(self):
		return self.pos.x

	def GetY(self):
		return self.pos.y

	def SetTag(self, tag):
		self.tag = tag

	def GetTag(self):
		return self.tag

	def SetID(self, ID):
		self.ID = ID

	def GetID(self):
		return self.ID

	def __str__(self):
		return str(self.GetTag()) + ": " + str(self.GetID()) + " at " + str(self.GetPos())
