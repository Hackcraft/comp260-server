'''
	Directions to language
	In future will support multiple different languages

	Class is not thread safe
'''
from Vector2 import Vector2

class Language:

	baseLanguage = "english"
	language = "english"
	languages = {}

	languages["english"] = {
		"direction":
		{
			"north": Vector2(0, 1),
			"north west": Vector2(-1, 1),
			"north east": Vector2(1, 1),

			"south": Vector2(0, -1),
			"south west": Vector2(-1, -1),
			"south east": Vector2(1, -1),

			"west": Vector2(-1, 0),
			"east": Vector2(1, 0)
		},
		"command":
		{
			"say": "say",
			"search": "search",

			"directions": "directions",
			"go": "go",
			"help": "help"
		}
	}

	# Keep a copy of the dictionary in reverse (tag : val) -> (val : tag)
	# for the current active language and the base language
	# which all other languages point to
	baseLanguageReversed = {}
	languageReversed = {}

	def __init__(self):
		Language.baseLanguageReversed = self.SetupReversedReference(self.baseLanguage)

	@staticmethod
	def ChangeLanguage(language):
		if language in Language.languages:
			Language.language = language
			Language.languageReversed = Language.SetupReversedReference(Language, language)

	def SetupReversedReference(self, language):
		languageReversed = {}
		# Copy the language - values in opposite order
		for category in self.languages[language]:
			languageReversed[category] = {
				v: k for k, v in self.languages[language][category].items()
			}
		return languageReversed

	# Returns the value associated with the word provided in the current selected language
	@staticmethod
	def WordToValue(category, word):
		if Language.language == Language.baseLanguage:
			return Language.BaseWordToValue(category, word)
		else:
			if word in Language.languages[Language.language][category]:
				baseWord = Language.languages[Language.language][category][word]
				if baseWord in Language.languages[Language.baseLanguage][category]:
					return Language.languages[Language.baseLanguage][category][baseWord]
		return None

	# Returns the value associated with the word provided in the base language
	@staticmethod
	def BaseWordToValue(category, word):
		if word in Language.languages[Language.baseLanguage][category]:
			return Language.languages[Language.baseLanguage][category][word]
		return None

	# Returns the word associated with the value provided in the current selected language
	@staticmethod
	def ValueToWord(category, value):
		if Language.language == Language.baseLanguage:
			return Language.ValueToBaseWord(category, value)
		else:
			if value in Language.baseLanguageReversed[category]:
				baseWord = Language.baseLanguageReversed[category][value]
				if baseWord in Language.languageReversed[category]:
					return Language.languageReversed[category][baseWord]
		return None

	# Returns the word associated with the value provided in the base language
	@staticmethod
	def ValueToBaseWord(category, value):
		if value in Language.baseLanguageReversed[category]:
			return Language.baseLanguageReversed[category][value]
		return None

Language()


