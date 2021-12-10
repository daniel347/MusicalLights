
class StaticHandler():

    def __init__(self, colours, controller, static_colour=(255, 255, 255)):
        self.controller = controller
        self.colours = colours

        self.current_colour = None
        self.set_uniform_colour(static_colour)
        self.is_stopped = False

    def set_uniform_colour(self, static_colour):
        self.current_colour = self.colours.make_uniform_colour_array(static_colour)

    def update_handler(self):
        self.controller.set_constant_colour(self.current_colour)

    def stop_playing(self):
        # Final change reached, end the sequence
        self.controller.turn_off_leds()