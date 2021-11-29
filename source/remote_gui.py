from TCPClient import TCPClient
from communcation_handler import ComHandler
from Enumerations import LightingModes
import math
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QMainWindow, QComboBox, QLabel, QVBoxLayout, QHBoxLayout, QSizePolicy, QSlider, QLayout, QFrame
from PyQt5.QtGui import QIcon, QPixmap, QColor, QImage, QPainter, QBrush, QPen
from PyQt5.QtCore import pyqtSlot, pyqtSignal, QRect, Qt, QSize

from functools import partial

button_styling = """
background-color: darkcyan;
font-family: Helvetica;
text-align: center;
border-radius: {};
"""

nav_bar_button_styling = """
background:none;
border:none;
margin:0;
padding:0;
"""

colour_display_styling = """
background-color: rgba({}, {}, {}, 1);
color: {};
font-family: Helvetica;
font-size: 14pt;
"""

slider_styling = """
QSlider::groove:horizontal {
    border: 0px solid;
    height: 16px;
    margin: 0px;
    border-radius: 8px;
    background-color: darkgrey;
}
QSlider::handle:horizontal {    
    background-color: darkcyan;
    border: 0px solid;
    height: 16px;
    width: 40px;
    border-radius: 8px;
    margin: 0px 0px;
}"""

colour_sequence_styling = """
QFrame#{} {{
    border: {} solid;
    border-color: darkcyan; 
    margin: 0pt;
    padding: -10pt;
    border-radius: 20px;
}}
"""

class FakeSocketClient():
    def __init__(self):
        pass

    def send(self, data):
        print(str(data))

    def receive(self, len):
        pass

    def close(self):
        pass

class LedState():

    def __init__(self, leds_running, mode, brightness=1, static_colour=(255, 255, 255), colour_sequence=None):
        self.leds_running = leds_running
        self.mode = mode
        self.brightness = brightness
        self.static_colour = static_colour
        self.colour_sequence = colour_sequence

class NavBarWidget(QWidget):

    # A signal to indicate the change of mode to other widgets
    mode_changed = pyqtSignal(int)

    def __init__(self, elements):
        super(NavBarWidget, self).__init__()

        self.selected_elem_index = 0
        self.layout = QHBoxLayout()
        self.layout.addStretch(1)
        self.setLayout(self.layout)

        self.setFixedHeight(100)

        self.element_list = []
        self.underline_list = []

        for i, element in enumerate(elements):
            v_layout = QVBoxLayout()
            label = QPushButton(element)
            label.clicked.connect(partial(self.click_nav_bar, new_mode=i))
            label.setStyleSheet(nav_bar_button_styling)
            label.setFixedWidth(200)

            underline = QLabel()
            underline.setFixedSize(200, 10)
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
    master_brightness_changed = pyqtSignal(float)
    led_running_toggled = pyqtSignal(bool)
    shutdown_triggered = pyqtSignal()

    def __init__(self, led_state):
        super(ControlWidget, self).__init__()
        self.led_state = led_state

        self.layout = QVBoxLayout()

        self.setLayout(self.layout)

        self.brightness_label = QLabel("Master Brightness")
        self.brightness_label.setAlignment(Qt.AlignHCenter)
        self.brightness_label.setFixedHeight(40)

        self.brightness_control = QSlider(Qt.Horizontal)
        self.brightness_control.setMaximumSize(QSize(600, 40))
        self.brightness_control.setMinimumSize(QSize(400, 40))
        self.brightness_control.setSliderPosition(100)
        self.brightness_control.setStyleSheet(slider_styling)
        self.brightness_control.valueChanged.connect(self.on_brightness_changed)

        self.layout.addWidget(self.brightness_label)
        self.layout.addWidget(self.brightness_control)

        self.toggle_leds = QPushButton()
        self.toggle_leds.setMaximumSize(QSize(500, 60))
        self.toggle_leds.setMinimumSize(QSize(300, 60))
        self.toggle_leds.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.toggle_leds.setText("Stop LEDS")
        self.toggle_leds.setStyleSheet(button_styling.format("10px"))
        self.layout.addWidget(self.toggle_leds)
        self.toggle_leds.clicked.connect(self.on_toggle_leds_running)

        self.shutdown = QPushButton()
        self.shutdown.setMaximumSize(QSize(500, 60))
        self.shutdown.setMinimumSize(QSize(300, 60))
        self.shutdown.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.shutdown.setText("Shutdown")
        self.shutdown.setStyleSheet(button_styling.format("10px"))
        self.shutdown.clicked.connect(self.on_shutdown_pressed)
        self.layout.addWidget(self.shutdown)

        self.layout.setAlignment(self.brightness_control, Qt.AlignHCenter)
        self.layout.setAlignment(self.toggle_leds, Qt.AlignHCenter)
        self.layout.setAlignment(self.shutdown, Qt.AlignHCenter)

    @pyqtSlot()
    def on_toggle_leds_running(self):
        if self.led_state.leds_running:
            self.toggle_leds.setText("Start LEDS")
        else:
            self.toggle_leds.setText("Stop LEDS")

        self.led_running_toggled.emit(not self.led_state.leds_running)

    @pyqtSlot(int)
    def on_brightness_changed(self, slider_value):
        self.master_brightness_changed.emit(float(slider_value/100))

    @pyqtSlot()
    def on_shutdown_pressed(self):
        self.shutdown_triggered.emit()


class ColourWheelWidget(QWidget):
    static_colour_selected = pyqtSignal(int, int, int)

    def __init__(self, image_path):
        super(ColourWheelWidget, self).__init__()

        size = 400
        self.setFixedSize(QSize(size, size))

        self.rgb_colour_wheel_img = QImage(image_path)
        self.rgb_colour_wheel = QLabel(self)
        self.rgb_colour_wheel.resize(size, size)

        self.scale = 456/size
        self.rgb_colour_wheel.setPixmap(QPixmap(image_path))
        self.rgb_colour_wheel.setScaledContents(True)
        self.rgb_colour_wheel.mousePressEvent = self.set_static_colour

        self.indicator_size = 20
        self.rgb_colour_indicator = QLabel(self)
        self.rgb_colour_indicator.move(size/2, size/2)
        self.rgb_colour_indicator.resize(self.indicator_size, self.indicator_size)
        self.rgb_colour_indicator.setStyleSheet("border: 5px solid darkgrey; border-radius: 8px;")

    def set_static_colour(self, event):
        x = event.pos().x()
        y = event.pos().y()
        self.rgb_colour_indicator.move(x - self.indicator_size/2, y - self.indicator_size/2)

        c = self.rgb_colour_wheel_img.pixel(int(x * self.scale),int(y * self.scale))  # color code (integer): 3235912
        c_rgb = QColor(c).getRgb()[0:-1]  # 8bit RGB: (255, 23, 255)

        self.static_colour_selected.emit(*c_rgb)


class StaticColourSelectionWidget(QWidget):
    def __init__(self, image_path):
        super(StaticColourSelectionWidget, self).__init__()

        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        self.colour_wheel = ColourWheelWidget(image_path)
        self.colour_wheel.static_colour_selected.connect(self.on_static_colour_select)

        self.colour_display = QLabel("#ffffff")
        self.colour_display.setMinimumSize(QSize(200, 200))
        self.colour_display.setMaximumSize(QSize(200, 200))
        self.colour_display.setStyleSheet(colour_display_styling.format(255, 255, 255, "black"))
        self.colour_display.setAlignment(Qt.AlignCenter)

        self.layout.addStretch(1)
        self.layout.addWidget(self.colour_wheel)
        self.layout.addWidget(self.colour_display)
        self.layout.addStretch(1)

    @pyqtSlot(int, int, int)
    def on_static_colour_select(self, r, g, b):
        colour_code = "#{}{}{}".format(hex(r)[2:], hex(g)[2:], hex(b)[2:])
        text_colour = "white" if (r * g * b)**(1/3) < 150 else "black"
        print((r * g * b)**(1/3))
        self.colour_display.setStyleSheet(colour_display_styling.format(r, g, b, text_colour))
        self.colour_display.setText(colour_code)


class ColourSequenceWidget(QFrame):

    colour_sequence_selected = pyqtSignal(int)

    def __init__(self, colour_sequence, sequence_enum):
        super(ColourSequenceWidget, self).__init__()
        self.sequence_enum = sequence_enum
        self.layout = QHBoxLayout()
        self.layout.setSpacing(0)
        self.setObjectName("sequence_frame")
        self.setLayout(self.layout)

        self.setStyleSheet(colour_sequence_styling.format("sequence_frame", "0px"))

        self.mousePressEvent = lambda x: self.colour_sequence_selected.emit(self.sequence_enum)


        for colour in colour_sequence:
            box = QLabel()
            box.setStyleSheet("background-color: rgba({}, {}, {}, 1);".format(colour[0], colour[1], colour[2]))
            self.layout.addWidget(box)

class SequenceSelectionWidget(QWidget):

    def __init__(self, colour_sequences):
        super(SequenceSelectionWidget, self).__init__()
        self.layout = QVBoxLayout()
        self.layout.setSpacing(20)
        self.setLayout(self.layout)

        self.sequence_widgets = []

        for i, sequence in enumerate(colour_sequences):
            seq_widget = ColourSequenceWidget(sequence, i)
            seq_widget.colour_sequence_selected.connect(self.on_sequence_select)
            self.sequence_widgets.append(seq_widget)
            self.layout.addWidget(seq_widget)

        self.layout.addStretch(1)

    @pyqtSlot(int)
    def on_sequence_select(self, selected_sequence):
        for seq_widget in self.sequence_widgets:
            seq_widget.setStyleSheet(colour_sequence_styling.format("sequence_frame", "0px"))

        self.sequence_widgets[selected_sequence].setStyleSheet(colour_sequence_styling.format("sequence_frame", "5px"))

class SpotifyWidget(QWidget):
    spotify_refresh_request = pyqtSignal()

    def __init__(self):
        super(SpotifyWidget, self).__init__()
        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignHCenter)
        self.setLayout(self.layout)

        spotify_logo_path = "../images/spotify_logo.png"
        self.spotify_logo = QLabel()
        self.spotify_logo.setPixmap(QPixmap(spotify_logo_path))
        self.spotify_logo.mousePressEvent = lambda x: self.spotify_refresh_request.emit()

        self.layout.addWidget(self.spotify_logo)

class Window(QMainWindow):

    def __init__(self, com_client, led_state, application):
        super(Window, self).__init__()
        self.handler = com_client
        self.led_state = led_state
        self.application = application  # not sure if this is a good idea

        self.main_widget = QWidget()
        self.overall_layout = QVBoxLayout()

        self.nav_bar = NavBarWidget([mode.name for mode in LightingModes])
        self.nav_bar.mode_changed.connect(self.on_change_mode)
        self.overall_layout.addWidget(self.nav_bar)

        self.mode_widgets = []

        # Static mode first ie LightingModes(0)
        colour_wheel_path = "../images/colour_wheel.png"
        static_colour_sel = StaticColourSelectionWidget(colour_wheel_path)
        static_colour_sel.colour_wheel.static_colour_selected.connect(self.on_static_colour_select)
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

        control_widget = ControlWidget(self.led_state)
        self.overall_layout.addWidget(control_widget)
        control_widget.led_running_toggled.connect(self.on_toggle_leds_running)
        control_widget.master_brightness_changed.connect(self.on_master_brightness_change)
        control_widget.shutdown_triggered.connect(self.on_shutdown_triggered)

        self.overall_layout.addStretch(1)

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

        self.led_state.mode = LightingModes(new_mode)
        self.handler.set_mode(new_mode)

    @pyqtSlot(int, int, int)
    def on_static_colour_select(self, r, g, b):
        self.led_state.static_colour = (r,g,b)
        self.handler.set_static_colour((r,g,b))

    @pyqtSlot(bool)
    def on_toggle_leds_running(self, leds_running):
        print(leds_running)
        self.led_state.leds_running = leds_running
        self.handler.set_leds_active(int(leds_running))

        if leds_running:
            self.nav_bar.setVisible(True)
            self.mode_widgets[self.led_state.mode.value].setVisible(True)
        else:
            self.nav_bar.setVisible(False)
            self.mode_widgets[self.led_state.mode.value].setVisible(False)

    @pyqtSlot(float)
    def on_master_brightness_change(self, brightness):
        self.handler.set_master_brightness(brightness)
        self.led_state.brightness = brightness

    @pyqtSlot()
    def on_shutdown_triggered(self):
        self.handler.shutdown()
        self.handler.client.close()
        self.application.exit(0)

    @pyqtSlot()
    def on_update_spotify(self):
        self.handler.shutdown()

if __name__ == '__main__':
    server_addr = "10.9.39.193"
    client = TCPClient(server_addr, 1237)
    # client = FakeSocketClient()
    handler = ComHandler(client)

    leds_running = True

    led_state = LedState(leds_running, LightingModes(0))

    app = QApplication([])
    window = Window(handler, led_state, app)
    app.exec_()

