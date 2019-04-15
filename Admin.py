from Vector2 import Vector2

class Admin():

	def __init__(self, password = "password"):
		self.__password = password


	def __str__(self):
		return str(self.tag) + ": " + str(self.id) + " at " + str(self.pos)