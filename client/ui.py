# input+output+command queue

# commands "clear" "connected" "disconnected"
import threading
from queue import Queue

import sys
import PyQt5.QtCore
import PyQt5.QtWidgets

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import QtCore

class UI:

    def __init__(self):
        self.input_queue = Queue()
        self.output_queue = Queue()
        self.command_queue = Queue()

        # Create UI
        self.initUI()

        # Update timer
        self.timer = QtCore.QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.timerEvent)
        self.timer.start()
        self.timer.start(100)

    def initUI(self):
        self.user_input = QLineEdit(self)
        self.user_input.setGeometry(10, 360, 580, 30)
        self.user_input.returnPressed.connect(self.on_submitted_input)

        self.chatOutput = QPlainTextEdit(self)
        self.chatOutput.setGeometry(10, 10, 580, 300)
        self.chatOutput.setReadOnly(True)

        self.setGeometry(300, 300, 600, 400)
        self.setWindowTitle('Multi user Dungeon | Not connected to server')
        self.show()

    def timerEvent(self):
        # Ui commands
        while self.command_queue.qsize() > 0:
            cmd = self.command_queue.get()
            if cmd == "clear":
                self.chatOutput.clear()
            elif cmd == "connected":
                self.setWindowTitle("Multi user Dungeon | Connected to server")
            elif cmd == "disconnected":
                self.setWindowTitle("Multi user Dungeon | Not connected to server")
        # Chat output
        if self.input_queue.qsize() > 0:
            self.chatOutput.appendPlainText(self.input_queue.get())

    def on_submitted_input(self):
        self.output_queue.put(self.user_input.text())
        self.user_input.setText("")
