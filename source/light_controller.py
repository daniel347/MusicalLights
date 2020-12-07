import neopixel
import board
import time

class LightController():

    def __init__(self, N_LEDS):
        self.N_LEDS = N_LEDS
        self.pixels = neopixel.NeoPixel(board.D18, N_LEDS, auto_write=False)

        self.MAX_CHANNEL = 255
        self.MIN_CHANNEL = 0

    def startup_pattern(self):
        """"Light pattern to play at startup"""
        start_pattern = [(50, 0, 0),
                         (75, 100, 0),
                         (0, 255, 0),
                         (0, 100, 75),
                         (0, 0, 50)]  # like a small spectrum wave

        speed = 0.01  # time delay between moving the wave up one pixel

        for wave_pos in range(self.N_LEDS - len(start_pattern)):
            self.pixels.fill((0, 0, 0))
            for i, c in enumerate(start_pattern):
                self.pixels[wave_pos + i] = c

            self.pixels.show()
            time.sleep(speed)

    def play_led_output(self, led_out):
        start_time = time.time()
        for change in led_out:
            if "led_array" in change:
                self.set_all_leds(change["led_array"])

            time.sleep(change["time"] + start_time - time.time())
            self.pixels.show()

    def set_all_leds(self, led_array):
        for i in range(self.N_LEDS):
            self.pixels[i] = led_array[i]

    def shutdown(self):
        self.set_all_leds([(0,0,0)] * self.N_LEDS)
        self.pixels.deinit()

