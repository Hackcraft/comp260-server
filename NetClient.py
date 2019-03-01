'''
	Class which talks to server
'''
import time

from NetBase import NetBase

def receiveThread(targetSocket):
	print("receiveThread Running")

class NetClient(NetBase):

	# Hooks
	hooks = { # tag : func
		"ConnectedToServer" : None,
		"DisconnectedFromServer" : None
	}

	def __init__(self):
		super().__init__()