from client import *
from PyQt5.QtWidgets import *
import sys
import threading
import hashlib
import time

# Building note:
# -m PyInstaller -y --noconsole

def main(ui):
    stopInput = True
    inLogin = True
    loginTag = LoginTags.ENTER_USERNAME
    salt = None
    initially_connected = False

    ip = "127.0.0.1"
    port = 8222

    while True:
        # Inital connection
        while not initially_connected:
            try:
                net = NetConnection(ip, port)
            except:
                ui.input_queue.put("Cannot connect to the server!")
                time.sleep(1)
                continue
            else:
                initially_connected = True
                ui.command_queue.put("clear")
                ui.command_queue.put("connected")

        # Reconnect
        if not net.is_connected():
            ui.command_queue.put("disconnected")
            try:
                net = NetConnection(ip, port)
            except:
                ui.input_queue.put("Trying to reconnect to server!")
                time.sleep(1)
            else:
                ui.command_queue.put("connected")
                ui.command_queue.put("clear")

        # Input from server
        while net.incoming_queue.qsize() > 0:
            tag, msg = DataPacket.separate(net.incoming_queue.get())

            # Handle Login state
            if tag is LoginTags.ENTER_USERNAME:
                loginTag = LoginTags.ENTER_USERNAME
                stopInput = False
                inLogin = True
                ui.input_queue.put("Enter username: ")

            elif tag is LoginTags.ENTER_PASSWORD:
                loginTag = LoginTags.ENTER_PASSWORD
                salt = msg
                inLogin = True
                ui.input_queue.put("Enter password: ")

            elif tag is LoginTags.BAD_PASSWORD:
                loginTag = LoginTags.ENTER_PASSWORD
                salt = msg
                inLogin = True
                ui.input_queue.put("Bad password!\nEnter password: ")

            # Handle Play state
            elif tag is DataTags.WRITE:
                inLogin = False
                ui.input_queue.put(msg)

            elif tag is DataTags.CLEAR:
                ui.command_queue.put("clear")

        # Input from client
        while ui.output_queue.qsize() > 0:
            msg = ui.output_queue.get()

            if stopInput:
                continue

            # Login state
            if inLogin:
                if loginTag is LoginTags.ENTER_USERNAME:
                    net.send(DataPacket.combine(LoginTags.CHECK_USERNAME, msg))

                elif loginTag is LoginTags.ENTER_PASSWORD:
                    salted = hashlib.sha512(msg.encode() + salt.encode()).hexdigest()
                    net.send(DataPacket.combine(LoginTags.CHECK_PASSWORD, salted))

            # Play state
            else:
                # Forward the messages to the server to process
                net.send(DataPacket.combine(DataTags.FORWARD, msg))

if __name__ == '__main__':

    # Create UI
    app = QApplication(sys.argv)
    ui = UI()

    # Create net
    currentBackgroundThread = threading.Thread(target=main, args=(ui,))
    currentBackgroundThread.start()

    sys.exit(app.exec_())

    # Create net connection in try
    # Net pass through thread