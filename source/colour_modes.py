import

class Colours():
    def __init__(self, num_leds):
        self.num_leds = 

    def colour_cycle_on_beat(self, colour_list, beats):
        led_out = []
        num_colours = len(colour_list)

        for i, beat in enumerate(beats):
            change_colour = {"time": beat["start"],
                             "led_array": colour_list[i % num_colours] * self.num_leds}
            led_out.append(change_colour)


