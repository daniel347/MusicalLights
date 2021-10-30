from TCPClient import TCPClient
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot

server_addr = "192.168.1.91"
client = TCPClient(server_addr, 1234)

leds_running = True

def window():
    app = QApplication(sys.argv)
    widget = QWidget()

    button1 = QPushButton(widget)
    button1.setText("Start LEDS")
    button1.move(100, 275)
    button1.resize(400, 50)
    button1.clicked.connect(button1_clicked)

    widget.setGeometry(200, 200, 600, 600)
    widget.setWindowTitle("PyQt5 Button Click Example")
    widget.show()
    sys.exit(app.exec_())


def button1_clicked():
    if leds_running:
        client.send(0x00)
    else:
        client.send(0x01)

    leds_running = not leds_running

if __name__ == '__main__':
    window()
