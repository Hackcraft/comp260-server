from Vector2 import Vector2

class Entity():

	def __init__(self):
		self.pos = Vector2(0, 0)
		self.tag = "unassigned"
		self.id = 0

	def __str__(self):
		return str(self.tag) + ": " + str(self.id) + " at " + str(self.pos)
