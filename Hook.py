'''
	Class to run functions off events
'''

import threading

class Hook:

	hooks = {}
	hooksLock = threading.RLock()  # Allow for recursive locking (hook.Run calling hook.Run etc....)

	def __init__(self):
		pass

	def Add(self, eventName, identifier, func):
		print("Adding: " + eventName)
		with self.hooksLock:
			if eventName not in self.hooks:
				self.hooks[eventName] = {}
			self.hooks[eventName][identifier] = func
		print("[hook add] Adding " + eventName + " " + identifier)

	def Run(self, eventName, args = ()):
		print("Running: " + eventName)
		output = None
		with self.hooksLock:
			print(eventName + " " + str(eventName in self.hooks))
			if eventName in self.hooks:
				output = None
				for identifier in self.hooks[eventName]:
					print("[hook run] " + eventName + " " + identifier)
					output = self.hooks[eventName][identifier](args)
					if output != None:
						break
		return output

	def Remove(self, eventName, identifier):
		print("Removing: " + eventName)
		with self.hooksLock:
			if eventName in self.hooks and identifier in self.hooks[eventName]:
				self.hooks[eventName][identifier] = None
				self.hooks[eventName].pop(identifier, None)

