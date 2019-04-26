'''
	Class to run functions off events
'''

import threading

class Hook:

	hooks = {}
	hooksLock = threading.Lock()

	def __init__(self):
		pass

	def Add(self, eventName, identifier, func):
		self.hooksLock.acquire()
		if not eventName in self.hooks:
			self.hooks[eventName] = {}
		self.hooks[eventName][identifier] = func
		self.hooksLock.release()
		print("Adding " + eventName + identifier)

	def Run(self, eventName, args = ()):
		output = None
		self.hooksLock.acquire()
		print("acquire?")
		print(str(eventName in self.hooks))
		if eventName in self.hooks:
			print("eventName in self.hooks?")
			output = None
			for identifier in self.hooks[eventName]:
				print(eventName + " " + identifier)
				output = self.hooks[eventName][identifier](args)
				if output != None:
					break
		self.hooksLock.release()
		return output

	def Remove(self, eventName, identifier):
		self.hooksLock.acquire()
		if eventName in self.hooks and identifier in self.hooks[eventName]:
			self.hooks[eventName][identifier] = None
			self.hooks[eventName].pop(identifier, None)
		self.hooksLock.release()

