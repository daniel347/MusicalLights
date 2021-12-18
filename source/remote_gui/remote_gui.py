from source.communication.TCPClient import TCPClient
from source.communication.communcation_handler import ComHandler
from source.Enumerations import LightingModes, colour_schemes
from source import Enumerations
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QMainWindow, \
    QLabel, QVBoxLayout, QHBoxLayout, QSizePolicy, QSlider, QFrame, QComboBox
from PyQt5.QtGui import QPixmap, QColor, QImage
from PyQt5.QtCore import pyqtSlot, pyqtSignal, Qt, QSize

from functools import partial
import gui_styling

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
            label.setStyleSheet(gui_styling.nav_bar_button_styling)
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

        self.line = QLabel()
        self.line.setFixedHeight(3)
        self.line.setFixedWidth(300)
        self.line.setStyleSheet("background-color: darkgray;")
        self.layout.addWidget(self.line, alignment=Qt.AlignHCenter)

        self.brightness_slider = LabelledSlider("Master Brightness", 0, 100, 1)
        self.brightness_slider.control.valueChanged.connect(self.on_brightness_changed)

        self.layout.addWidget(self.brightness_slider, alignment=Qt.AlignHCenter)

        self.toggle_leds = QPushButton()
        self.toggle_leds.setMaximumSize(QSize(500, 60))
        self.toggle_leds.setMinimumSize(QSize(300, 60))
        self.toggle_leds.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.toggle_leds.setText("Stop LEDS")
        self.toggle_leds.setStyleSheet(gui_styling.button_styling.format("10px"))
        self.layout.addWidget(self.toggle_leds, alignment=Qt.AlignHCenter)
        self.toggle_leds.clicked.connect(self.on_toggle_leds_running)

        self.shutdown = QPushButton()
        self.shutdown.setMaximumSize(QSize(500, 60))
        self.shutdown.setMinimumSize(QSize(300, 60))
        self.shutdown.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.shutdown.setText("Shutdown")
        self.shutdown.setStyleSheet(gui_styling.button_styling.format("10px"))
        self.shutdown.clicked.connect(self.on_shutdown_pressed)
        self.layout.addWidget(self.shutdown, alignment=Qt.AlignHCenter)

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

    def __init__(self):
        super(ColourWheelWidget, self).__init__()

        size = 400
        self.setFixedSize(QSize(size, size))
        colour_wheel_path = "remote_gui/colour_wheel.png"

        self.rgb_colour_wheel_img = QImage(colour_wheel_path)
        self.rgb_colour_wheel = QLabel(self)
        self.rgb_colour_wheel.resize(size, size)

        self.scale = 456/size
        self.rgb_colour_wheel.setPixmap(QPixmap(colour_wheel_path))
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
    def __init__(self):
        super(StaticColourSelectionWidget, self).__init__()

        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        self.colour_wheel = ColourWheelWidget()
        self.colour_wheel.static_colour_selected.connect(self.on_static_colour_select)

        self.colour_display = QLabel("#ffffff")
        self.colour_display.setMinimumSize(QSize(200, 200))
        self.colour_display.setMaximumSize(QSize(200, 200))
        self.colour_display.setStyleSheet(gui_styling.colour_display_styling.format(255, 255, 255, "black"))
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
        self.colour_display.setStyleSheet(gui_styling.colour_display_styling.format(r, g, b, text_colour))
        self.colour_display.setText(colour_code)


class ColourSequenceWidget(QFrame):

    colour_sequence_selected = pyqtSignal(str)

    def __init__(self, colour_sequence, sequence_name):
        super(ColourSequenceWidget, self).__init__()
        self.sequence_name = sequence_name
        self.layout = QHBoxLayout()
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0,0,0,0)
        self.setObjectName("sequence_frame")
        self.setLayout(self.layout)

        self.setStyleSheet(gui_styling.colour_sequence_styling.format("sequence_frame", "0px"))

        self.mousePressEvent = lambda x: self.colour_sequence_selected.emit(self.sequence_name)

        for colour in colour_sequence:
            box = QLabel()
            box.setMinimumHeight(50)
            box.setStyleSheet("background-color: rgba({}, {}, {}, 1);".format(colour[0], colour[1], colour[2]))
            self.layout.addWidget(box)

class LabelledSlider(QWidget):

    def __init__(self, label_name, min_val, max_val, tick_int):
        super(LabelledSlider, self).__init__()
        self.layout = QVBoxLayout()
        self.layout.setSpacing(5)
        self.setLayout(self.layout)

        self.label = QLabel(label_name)
        self.label.setAlignment(Qt.AlignHCenter)
        self.label.setFixedHeight(40)

        self.control = QSlider(Qt.Horizontal)
        self.control.setMaximumSize(QSize(600, 40))
        self.control.setMinimumSize(QSize(400, 40))
        self.control.setMaximum(max_val)
        self.control.setMinimum(min_val)
        self.control.setSliderPosition(max_val)
        self.control.setTickInterval(tick_int)
        self.control.setStyleSheet(gui_styling.slider_styling)

        self.layout.addWidget(self.label, alignment=Qt.AlignHCenter)
        self.layout.addWidget(self.control, alignment=Qt.AlignHCenter)

class SequenceSelectionWidget(QWidget):
    sequence_period_changed = pyqtSignal(int)
    colour_mode_changed = pyqtSignal(str)

    def __init__(self, colour_sequences):
        super(SequenceSelectionWidget, self).__init__()
        self.layout = QVBoxLayout()
        self.layout.setSpacing(20)
        self.setLayout(self.layout)

        self.sequence_widgets = []

        for name, sequence in colour_sequences.items():
            seq_widget = ColourSequenceWidget(sequence, name)
            seq_widget.colour_sequence_selected.connect(self.on_sequence_select)
            self.sequence_widgets.append(seq_widget)
            self.layout.addWidget(seq_widget)

        self.layout.addStretch(1)

        self.period_slider = LabelledSlider("Period", 100, 5000, 100)
        self.period_slider.control.valueChanged.connect(self.on_period_changed)
        self.layout.addWidget(self.period_slider, alignment=Qt.AlignHCenter)

        self.colour_change_mode = QComboBox()
        self.colour_change_mode.addItems(Enumerations.colour_functions)
        self.colour_change_mode.setStyleSheet(gui_styling.mode_selection_styling)
        self.colour_change_mode.currentIndexChanged.connect(self.on_colour_mode_change)
        self.layout.addWidget(self.colour_change_mode, alignment=Qt.AlignHCenter)

    @pyqtSlot(str)
    def on_sequence_select(self, selected_sequence):
        for seq_widget in self.sequence_widgets:
            if seq_widget.sequence_name == selected_sequence:
                seq_widget.setStyleSheet(gui_styling.colour_sequence_styling.format("sequence_frame", "5px"))
            else:
                seq_widget.setStyleSheet(gui_styling.colour_sequence_styling.format("sequence_frame", "0px"))

    def get_all_signals(self):
        # Returns the signals from each of the sequences
        return [seq_widget.colour_sequence_selected
                for seq_widget in self.sequence_widgets]

    @pyqtSlot(int)
    def on_period_changed(self, period):
        self.sequence_period_changed.emit(period)

    @pyqtSlot(int)
    def on_colour_mode_change(self, mode_ind):
        self.colour_mode_changed.emit(Enumerations.colour_functions[mode_ind])

class SpotifyWidget(QWidget):
    spotify_refresh_request = pyqtSignal()

    def __init__(self):
        super(SpotifyWidget, self).__init__()
        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignHCenter)
        self.setLayout(self.layout)

        spotify_logo_path = r"remote_gui\spotify_logo.png"
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
        static_colour_sel = StaticColourSelectionWidget()
        static_colour_sel.colour_wheel.static_colour_selected.connect(self.on_static_colour_select)
        self.mode_widgets.append(static_colour_sel)
        self.overall_layout.addWidget(static_colour_sel)

        # Then the sequence mode LightingModes(1)
        sequence_sel = SequenceSelectionWidget(colour_schemes)
        self.mode_widgets.append(sequence_sel)
        self.overall_layout.addWidget(sequence_sel)
        for signal in sequence_sel.get_all_signals():
            signal.connect(self.on_sequence_colour_select)
        sequence_sel.setVisible(False)

        sequence_sel.sequence_period_changed.connect(self.on_sequence_period_changed)
        sequence_sel.colour_mode_changed.connect(self.on_colour_change_mode_changed)

        # them the spotify widget LightingModes(2)
        spotify_wid = SpotifyWidget()
        spotify_wid.spotify_refresh_request.connect(self.on_update_spotify)
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

    @pyqtSlot(str)
    def on_sequence_colour_select(self, sequence_name):
        self.handler.set_colour_sequence(sequence_name)

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

    @pyqtSlot(int)
    def on_sequence_period_changed(self, period):
        self.handler.set_sequence_period(period)

    @pyqtSlot(str)
    def on_colour_change_mode_changed(self, colour_change_mode):
        self.handler.set_colour_change_mode(colour_change_mode)

if __name__ == '__main__':
    server_addr = '192.168.1.146' # "10.9.39.193"
    # client = TCPClient(server_addr, 1237)
    client = FakeSocketClient()
    handler = ComHandler(client)

    leds_running = True

    led_state = LedState(leds_running, LightingModes(0))

    app = QApplication([])
    window = Window(handler, led_state, app)
    app.exec_()

