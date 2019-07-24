from client import *
from PyQt5.QtWidgets import *
import sys
import threading
import hashlib

def main(ui):
    stopInput = True
    inLogin = True
    loginTag = LoginTags.ENTER_USERNAME
    salt = None

    try:
        net = NetConnection()
    except:
        ui.input_queue.put("Cannot connect to the server! (relaunch to try again)")
        return
    else:
        ui.command_queue.put("connected")

    while True:
        if not net.is_connected():
            ui.command_queue.put("disconnected")
            ui.input_queue.put("Restart client to reconnect!")

        # Input from server
        while net.incoming_queue.qsize() > 0:
            tag, msg = DataPacket.separate(net.incoming_queue.get())

            # Handle Login state
            if tag is LoginTags.ENTER_USERNAME:
                loginTag = LoginTags.ENTER_USERNAME
                stopInput = False
                ui.input_queue.put("Enter username: ")

            elif tag is LoginTags.ENTER_PASSWORD:
                loginTag = LoginTags.ENTER_PASSWORD
                salt = msg
                ui.input_queue.put("Enter password: ")

            elif tag is LoginTags.BAD_PASSWORD:
                loginTag = LoginTags.ENTER_PASSWORD
                salt = msg
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

            print(msg)

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