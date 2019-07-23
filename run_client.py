from client import *
from PyQt5.QtWidgets import *
import sys
import threading

def main(ui):
    try:
        netCon = NetConnection()
    except:
        ui.input_queue.put("Cannot connect to the server! (relaunch to try again)")
    else:
        ui.command_queue.put("connected")
    while True:
        while ui.output_queue.qsize() > 0:
            msg = ui.output_queue.get()
            print(msg)
            ui.input_queue.put(msg)

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