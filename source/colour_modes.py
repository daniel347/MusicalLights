class Colours:
    def __init__(self, N_LEDS):
        self.N_LEDS = N_LEDS

    def colour_change_on_beat(self, colour_list, beats):
        led_out = []
        num_colours = len(colour_list)

        for i, beat in enumerate(beats):
            change_colour = {"time": beat["start"],
                             "led_array": colour_list[i % num_colours] * self.N_LEDS}
            led_out.append(change_colour)

        return led_out


