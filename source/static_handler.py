import numpy as np

import time


class StaticHandler():

    def __init__(self, colours, mood_colours, controller):
        self.controller = controller
        self.colours = colours
        self.mood_colours = mood_colours

    def update_handler(self):
        pass

    def stop_playing(self):
        # Final change reached, end the sequence
        self.controller.turn_off_leds()