from client import *
from PyQt5.QtWidgets import *
import sys
import threading
import hashlib
import time

# Building note:
# -m PyInstaller -y --noconsole

def main(ui):
    stop_input = True
    in_login = True
    login_tag = LoginTags.ENTER_USERNAME
    salt = None
    initially_connected = False

    ip = "127.0.0.1"
    port = 8222

    while not ui.should_close:
        # Inital connection
        while not initially_connected:
            try:
                net = NetConnection(ip, port)
            except:
                stop_input = True
                ui.input_queue.put("Cannot connect to the server!")
                time.sleep(1)
                continue
            else:
                initially_connected = True
                ui.command_queue.put("clear")
                ui.command_queue.put("connected")

        # Input from server
        while net.incoming_queue.qsize() > 0:
            tag, msg = DataPacket.separate(net.incoming_queue.get())

            # Handle Login state
            if tag is LoginTags.ENTER_USERNAME:
                login_tag = LoginTags.ENTER_USERNAME
                stop_input = False
                in_login = True
                ui.input_queue.put("Enter username: ")

            elif tag is LoginTags.ENTER_PASSWORD:
                login_tag = LoginTags.ENTER_PASSWORD
                salt = msg
                in_login = True
                ui.input_queue.put("Enter password: ")

            elif tag is LoginTags.BAD_PASSWORD:
                login_tag = LoginTags.ENTER_PASSWORD
                salt = msg
                in_login = True
                ui.input_queue.put("Bad password!\nEnter password: ")

            # Handle Play state
            elif tag is DataTags.WRITE:
                in_login = False
                ui.input_queue.put(msg)

            elif tag is DataTags.CLEAR:
                ui.command_queue.put("clear")

            elif tag is DataTags.DUPLICATE_LOGIN:
                ui.input_queue.put(msg)
                time.sleep(1)

        # Reconnect
        if not net.is_connected():
            ui.command_queue.put("disconnected")
            try:
                net = NetConnection(ip, port)
            except:
                stop_input = True
                ui.input_queue.put("Trying to reconnect to server!")
                time.sleep(1)
                continue
            else:
                ui.command_queue.put("connected")
                ui.command_queue.put("clear")

        # Input from client
        while ui.output_queue.qsize() > 0:
            msg = ui.output_queue.get()

            if stop_input:
                continue

            # Login state
            if in_login:
                if login_tag is LoginTags.ENTER_USERNAME:
                    net.send(DataPacket.combine(LoginTags.CHECK_USERNAME, msg))

                elif login_tag is LoginTags.ENTER_PASSWORD:
                    salted = hashlib.sha512(msg.encode() + salt.encode()).hexdigest()
                    net.send(DataPacket.combine(LoginTags.CHECK_PASSWORD, salted))

            # Play state
            else:
                # Forward the messages to the server to process
                net.send(DataPacket.combine(DataTags.FORWARD, msg))

    if net is not None:
        net.close()

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