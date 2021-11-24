from TCPClient import TCPClient
from communcation_handler import ComHandler
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QMainWindow, QComboBox
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot

class FakeHandler():

    def __init__(self):
        pass

    def set_leds_active(self, active):
        print("setting led active to : {}".format(active))

    def set_mode(self, mode):
        print("Setting mode to : {}".format(mode))


class LedState():

    def __init__(self, leds_running, modes):
        self.leds_running = leds_running
        self.modes = modes

        self.current_mode = modes[0]


class Window(QMainWindow):

    @pyqtSlot()
    def toggle_leds_clicked(self):
        if self.led_state.leds_running:
            self.handler.set_leds_active(0)
            self.toggle_leds.setText("Start LEDS")
        else:
            self.handler.set_leds_active(1)
            self.toggle_leds.setText("Stop LEDS")

        self.led_state.leds_running = not self.led_state.leds_running

    def mode_change(self, i):
        self.led_state.current_mode = self.mode_dropdown.itemText(i)
        self.handler.set_mode(i)


    def __init__(self, com_client, led_state):
        super(Window, self).__init__()
        self.handler = com_client
        self.led_state = led_state

        self.widget = QWidget()

        self.mode_dropdown = QComboBox(self.widget)
        self.mode_dropdown.addItems(self.led_state.modes)
        self.mode_dropdown.currentIndexChanged.connect(self.mode_change)
        self.mode_dropdown.move(200, 200)
        self.mode_dropdown.resize(200, 50)

        self.toggle_leds = QPushButton(self.widget)
        self.toggle_leds.setText("Stop LEDS")
        self.toggle_leds.move(100, 275)
        self.toggle_leds.resize(400, 50)
        self.toggle_leds.clicked.connect(self.toggle_leds_clicked)

        self.widget.setGeometry(200, 200, 600, 600)
        self.widget.setWindowTitle("PyQt5 Button Click Example")
        self.widget.show()


if __name__ == '__main__':
    server_addr = "10.9.39.193"
    client = TCPClient(server_addr, 1237)
    handler = ComHandler(client)
    # handler = FakeHandler()

    leds_running = True

    led_state = LedState(leds_running, ["Constant", "Sequence", "Music"])

    app = QApplication([])
    window = Window(handler, led_state)
    app.exec_()

