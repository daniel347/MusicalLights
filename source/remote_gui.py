from TCPClient import TCPClient
from communcation_handler import ComHandler
from Enumerations import LightingModes
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QMainWindow, QComboBox, QLabel, QVBoxLayout, QHBoxLayout, QSizePolicy, QSlider, QLayout
from PyQt5.QtGui import QIcon, QPixmap, QColor, QImage, QPainter, QBrush, QPen
from PyQt5.QtCore import pyqtSlot, pyqtSignal, QRect, Qt, QSize

from functools import partial

button_styling = "background-color: darkcyan;" \
                 "font-family: Helvetica;" \
                 "text-align: center;" \
                 "border-radius: {};" \

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

    # A signal to indicate the change of mode to other widgets
    mode_changed = pyqtSignal(int)

    def __init__(self, elements):
        super(NavBarWidget, self).__init__()

        self.selected_elem_index = 0

        self.layout = QHBoxLayout()
        self.layout.addStretch(1)
        self.setLayout(self.layout)

        self.element_list = []
        self.underline_list = []

        for i, element in enumerate(elements):
            v_layout = QVBoxLayout()
            label = QPushButton(element)
            label.clicked.connect(partial(self.click_nav_bar, new_mode=i))
            label.setStyleSheet("background:none;border:none;margin:0;padding:0;")
            label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            label.setMinimumSize(QSize(200, 30))

            underline = QLabel()
            underline.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            underline.setMinimumSize(QSize(200, 5))
            underline.setStyleSheet("background-color: black")
            if i != self.selected_elem_index:
                underline.setVisible(False)

            v_layout.addWidget(label)
            v_layout.addWidget(underline)
            self.layout.addLayout(v_layout)
            self.layout.addStretch(1)

            self.element_list.append(label)
            self.underline_list.append(underline)

    @pyqtSlot()
    def click_nav_bar(self, new_mode):
        print("Changed to mode {}".format(new_mode))
        for underline in self.underline_list:
            underline.setVisible(False)

        self.underline_list[new_mode].setVisible(True)
        self.mode_changed.emit(new_mode)

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
        self.toggle_leds.resize(500, 300)
        self.toggle_leds.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        self.toggle_leds.setText("Stop LEDS")
        self.toggle_leds.setStyleSheet(button_styling.format("10px"))
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

    @pyqtSlot(int)
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


class StaticColourSelectionWidget(QWidget):
    def __init__(self, handler, led_state, image_path):
        super(StaticColourSelectionWidget, self).__init__()

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


class ColourSequenceWidget(QWidget):

    def __init__(self, colour_sequence):
        super(ColourSequenceWidget, self).__init__()
        self.layout = QHBoxLayout()
        self.layout.setSpacing(0)
        self.setLayout(self.layout)

        for colour in colour_sequence:
            box = QLabel()
            box.setMaximumSize(QSize(500, 150))
            box.setStyleSheet("background-color: rgba({}, {}, {}, 1);".format(colour[0], colour[1], colour[2]))
            self.layout.addWidget(box)

class SequenceSelectionWidget(QWidget):

    def __init__(self, colour_sequences):
        super(SequenceSelectionWidget, self).__init__()
        self.layout = QVBoxLayout()
        self.layout.setSpacing(20)
        self.setLayout(self.layout)

        for sequence in colour_sequences:
            seq_widget = ColourSequenceWidget(sequence)
            self.layout.addWidget(seq_widget)

        self.layout.addStretch(1)

class SpotifyWidget(QWidget):

    def __init__(self):
        super(SpotifyWidget, self).__init__()
        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignHCenter)
        self.setLayout(self.layout)

        spotify_logo_path = "../images/spotify_logo.png"
        self.spotify_logo = QLabel()
        self.spotify_logo.setPixmap(QPixmap(spotify_logo_path))
        self.layout.addWidget(self.spotify_logo)

        self.refresh_button = QPushButton("Refresh")
        self.layout.addWidget(self.refresh_button)

class Window(QMainWindow):

    def __init__(self, com_client, led_state):
        super(Window, self).__init__()
        self.handler = com_client
        self.led_state = led_state

        self.main_widget = QWidget()
        self.overall_layout = QVBoxLayout()

        nav_bar = NavBarWidget([mode.name for mode in LightingModes])
        nav_bar.mode_changed.connect(self.on_change_mode)
        self.overall_layout.addWidget(nav_bar)

        self.mode_widgets = []

        # Static mode first ie LightingModes(0)
        colour_wheel_path = "../images/colour_wheel.png"
        static_colour_sel = StaticColourSelectionWidget(self.handler, self.led_state, colour_wheel_path)
        self.mode_widgets.append(static_colour_sel)
        self.overall_layout.addWidget(static_colour_sel)

        # Then the sequence mode LightingModes(1)
        sequence_sel = SequenceSelectionWidget([[[255, 0, 0], [0, 255, 0], [0, 0, 255]], [[255, 255, 0], [0, 255, 255], [255, 0, 255]]])
        self.mode_widgets.append(sequence_sel)
        self.overall_layout.addWidget(sequence_sel)
        sequence_sel.setVisible(False)

        # them the spotify widget LightingModes(2)
        spotify_wid = SpotifyWidget()
        self.mode_widgets.append(spotify_wid)
        self.overall_layout.addWidget(spotify_wid)
        spotify_wid.setVisible(False)

        control_widget = ControlWidget(self.handler, self.led_state)
        self.overall_layout.addWidget(control_widget)

        self.main_widget.setLayout(self.overall_layout)
        self.main_widget.setGeometry(200, 200, 600, 600)
        self.main_widget.setWindowTitle("LED Strip Control")
        self.main_widget.show()

    @pyqtSlot(int)
    def on_change_mode(self, new_mode):
        for i, widget in enumerate(self.mode_widgets):
            if i == new_mode:
                widget.setVisible(True)
            else:
                widget.setVisible(False)




if __name__ == '__main__':
    server_addr = "10.9.39.193"
    # client = TCPClient(server_addr, 1237)
    # handler = ComHandler(client)
    handler = FakeHandler()

    leds_running = True

    led_state = LedState(leds_running, [mode.name for mode in LightingModes])

    app = QApplication([])
    window = Window(handler, led_state)
    app.exec_()

