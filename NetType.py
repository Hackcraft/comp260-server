class NetType:
	tag = None

#	def __init__(self):
#		pass

	@classmethod
	def ToNetString(cls, obj):
		raise NotImplementedError()

	@classmethod
	def FromNetString(cls, string):
		raise NotImplementedError()

	# Return the first word(tag) in a string
	@classmethod
	def DataTag(cls, string):
		return string.split(' ')[0].strip()

	# Return all but the first word(tag) in a string
	@classmethod
	def StripTag(cls, string):
		separatedStrings = string.split(' ')
		separatedStrings.pop(0)
		return ' '.join(separatedStrings)