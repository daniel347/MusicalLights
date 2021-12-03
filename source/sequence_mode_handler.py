
class SequenceHandler():

    def __init__(self, colours, controller, colour_scheme, period,
                 mode="colour_fade_on_beat", duty_cycle=0.5):
        self.controller = controller
        self.colours = colours
        self.colour_scheme = colour_scheme
        self.period = period
        self.mode = mode
        self.duty_cycle = duty_cycle

        self.sequence = None

    def generate_beats(self):
        beats = []
        for i in range(len(self.colours.colour_schemes[self.colour_scheme])):
            beats.append({"start": i * self.period,
                          "duration": self.duty_cycle * self.period,
                          "confidence": 1})
        return beats

    def generate_sequence(self):
        beats = self.generate_beats()
        self.sequence = getattr(self.colours, self.mode)\
            (self.colours.colour_schemes[self.colour_scheme], beats)

    def update_handler(self):

        if not self.controller.is_playing_sequence():
            self.controller.start_playing_sequence(self.sequence)

        ret = self.controller.update_playing_sequence()
        if ret == 2:
            # Final change reached, end the sequence
            # If main calls update handler again then the sequence
            # will loop over from the beginning
            self.controller.end_playing_sequence()

    def stop_playing(self):
        self.controller.end_playing_sequence()
        self.controller.turn_off_leds()
