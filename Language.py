'''
	Directions to language
	In future will support multiple different languages
	In future will read txt file
'''
from Vector2 import Vector2

class Language:

	languages = {}

	languages["english"] = {
		"north" : Vector2(0, 1),
		"north west" : Vector2(-1, 1),
		"north east" : Vector2(1, 1),

		"south" : Vector2(0, -1),
		"south west" : Vector2(-1, -1),
		"south east" : Vector2(1, -1),

		"west" : Vector2(-1, 0),
		"east" : Vector2(1, 0)
	}

	# Keep a copy of the dictionary in reverse (tag : val) -> (val : tag)
	languagesInverse = {}
	for language in languages:
		languagesInverse[language] = {v: k for k, v in languages[language].items()}

	def __init__(self, language = "english"):
		self.ChangeLanguage(language)

	def ChangeLanguage(self, language = "english"):
		if language in self.languages:
			self.language = language

	def WordToValue(self, stringDir):
		return self.languages[self.language][stringDir]

	def ValueToWord(self, value):
		return self.languagesInverse[self.language][value]


