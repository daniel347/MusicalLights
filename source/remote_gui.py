from TCPClient import TCPClient
from communcation_handler import ComHandler
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QMainWindow, QComboBox, QLabel, QVBoxLayout, QHBoxLayout, QSizePolicy, QSlider
from PyQt5.QtGui import QIcon, QPixmap, QColor, QImage, QPainter, QBrush, QPen
from PyQt5.QtCore import pyqtSlot, QRect, Qt, QSize


class FakeHandler():

    def __init__(self):
        pass

    def set_leds_active(self, active):
        print("setting led active to : {}".format(active))

    def set_mode(self, mode):
        print("Setting mode to : {}".format(mode))

    def set_static_colour(self, colour):
        print("Setting static colour to {}".format(colour))


class LedState():

    def __init__(self, leds_running, modes):
        self.leds_running = leds_running
        self.modes = modes

        self.current_mode = modes[0]

class NavBarWidget(QWidget):
    def __init__(self, elements):
        super(NavBarWidget, self).__init__()

        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        self.element_list = []
        self.underline_list = []

        for element in elements:
            v_layout = QVBoxLayout()
            label = QLabel(element)
            label.setAlignment(Qt.AlignHCenter)

            underline = QLabel()
            underline.setMaximumSize(QSize(200, 5))
            underline.resize(200, 5)
            underline.setStyleSheet("background-color: black")

            v_layout.addWidget(label)
            v_layout.addWidget(underline)
            self.layout.addLayout(v_layout)

            self.element_list.append(label)
            self.underline_list.append(underline)

class ControlWidget(QWidget):
    def __init__(self, handler, led_state):
        super(ControlWidget, self).__init__()
        self.handler = handler
        self.led_state = led_state

        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignHCenter)
        self.setLayout(self.layout)

        """
        self.mode_dropdown = QComboBox()
        self.mode_dropdown.addItems(self.led_state.modes)
        self.mode_dropdown.currentIndexChanged.connect(self.mode_change)
        self.mode_dropdown.setMaximumSize(QSize(200, 100))
        self.layout.addWidget(self.mode_dropdown)
        """

        self.brightness_label = QLabel("Master Brightness")
        self.brightness_label.setAlignment(Qt.AlignHCenter)

        self.slider_hbox = QHBoxLayout()
        self.slider_hbox.setAlignment(Qt.AlignHCenter)

        self.dark_icon = QLabel()
        self.dark_icon.setPixmap(QPixmap("../images/light_bulb.png"))
        self.dark_icon.setScaledContents(True)
        self.dark_icon.setMaximumSize(QSize(40, 40))

        self.light_icon = QLabel()
        self.light_icon.setPixmap(QPixmap("../images/light_bulb.png"))
        self.light_icon.setScaledContents(True)
        self.light_icon.setMaximumSize(QSize(40, 40))

        self.brightness_control = QSlider(Qt.Horizontal)
        self.brightness_control.setMaximumSize(QSize(500, 40))

        self.slider_hbox.addWidget(self.dark_icon)
        self.slider_hbox.addWidget(self.brightness_control)
        self.slider_hbox.addWidget(self.light_icon)


        self.layout.addWidget(self.brightness_label)
        self.layout.addLayout(self.slider_hbox)


        self.toggle_leds = QPushButton()
        self.toggle_leds.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Maximum)
        self.toggle_leds.setText("Stop LEDS")
        self.layout.addWidget(self.toggle_leds)
        self.toggle_leds.clicked.connect(self.toggle_leds_clicked)

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


class ColourWheelWidget(QWidget):
    def __init__(self, handler, led_state, image_path):
        super(ColourWheelWidget, self).__init__()

        self.handler = handler
        self.led_state = led_state
        self.setMinimumSize(QSize(400, 400))

        self.rgb_colour_wheel_img = QImage(image_path)
        self.rgb_colour_wheel = QLabel(self)
        self.rgb_colour_wheel.resize(400, 400)
        self.scale = 456/200
        self.rgb_colour_wheel.setPixmap(QPixmap(image_path))
        self.rgb_colour_wheel.setScaledContents(True)
        self.rgb_colour_wheel.mousePressEvent = self.set_static_colour

        self.rgb_colour_indicator = QLabel('colour_indicator', self)
        self.rgb_colour_indicator.move(100, 100)
        self.rgb_colour_indicator.resize(20, 20)
        self.rgb_colour_indicator.setStyleSheet("border: 3px solid black; border-radius: 10px;")

    def set_static_colour(self, event):
        x = event.pos().x()
        y = event.pos().y()
        self.rgb_colour_indicator.move(x, y)

        c = self.rgb_colour_wheel_img.pixel(int(x * self.scale),int(y * self.scale))  # color code (integer): 3235912
        c_rgb = QColor(c).getRgb()[0:-1]  # 8bit RGB: (255, 23, 255)

        self.handler.set_static_colour(c_rgb)


class ColourSelectionWidget(QWidget):
    def __init__(self, handler, led_state, image_path):
        super(ColourSelectionWidget, self).__init__()

        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        self.colour_wheel = ColourWheelWidget(handler, led_state, image_path)

        self.colour_display = QLabel()
        self.colour_display.setMinimumSize(QSize(200, 200))
        self.colour_display.setMaximumSize(QSize(200, 200))
        self.colour_display.setStyleSheet("background-color: red")

        self.layout.addStretch(1)
        self.layout.addWidget(self.colour_wheel)
        self.layout.addWidget(self.colour_display)
        self.layout.addStretch(1)


class Window(QMainWindow):

    def __init__(self, com_client, led_state):
        super(Window, self).__init__()
        self.handler = com_client
        self.led_state = led_state

        self.main_widget = QWidget()

        self.overall_layout = QVBoxLayout()

        nav_bar = NavBarWidget(["Static", "Sequence", "Spotify"])
        self.overall_layout.addWidget(nav_bar)

        image_path = "../images/colour_wheel.png"
        colour_sel = ColourSelectionWidget(self.handler, self.led_state, image_path)
        self.overall_layout.addWidget(colour_sel)

        control_widget = ControlWidget(self.handler, self.led_state)
        self.overall_layout.addWidget(control_widget)

        self.main_widget.setLayout(self.overall_layout)
        self.main_widget.setGeometry(200, 200, 600, 600)
        self.main_widget.setWindowTitle("Why wont this work")
        self.main_widget.show()


if __name__ == '__main__':
    server_addr = "10.9.39.193"
    # client = TCPClient(server_addr, 1237)
    # handler = ComHandler(client)
    handler = FakeHandler()

    leds_running = True

    led_state = LedState(leds_running, ["Constant", "Sequence", "Music"])

    app = QApplication([])
    window = Window(handler, led_state)
    app.exec_()

