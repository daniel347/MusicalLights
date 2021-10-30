import neopixel
import board
import time
import math
import RPi.GPIO as GPIO
import numpy as np
from scipy.interpolate import interp1d

class LightController():

    def __init__(self, N_LEDS, LEDS_PER_COLOUR):
        self.N_LEDS = N_LEDS
        self.LEDS_PER_COLOUR = LEDS_PER_COLOUR
        self.pixels = neopixel.NeoPixel(board.D18, N_LEDS, auto_write=False)

        self.MAX_CHANNEL = 255
        self.MIN_CHANNEL = 0

        # variables to handle playing a song
        self.song_start_time = 0.0
        self.sequence_playing = None
        self.sequence_index = 0
        self.max_sequence_index = 0

    def startup_pattern(self):
        """"Light pattern to play at startup"""
        start_pattern = [(50, 0, 0), (75, 100, 0), (0, 255, 0), (0, 100, 75),
                         (0, 0, 50)]  # like a small spectrum wave

        speed = 0.0025  # time delay between moving the wave up one pixel

        for wave_pos in range(self.N_LEDS - len(start_pattern)):
            self.pixels.fill((0, 0, 0))
            for i, c in enumerate(start_pattern):
                self.pixels[wave_pos + i] = c

            self.pixels.show()
            time.sleep(speed)

    def start_playing_sequence(self, light_sequence, track_pos = 0.0):
        self.song_start_time = time.time() - track_pos
          # take the first change time after the start pos
        self.sequence_index = 0
        while light_sequence.change_times[self.sequence_index] < track_pos:
            self.sequence_index += 1
            
        self.sequence_playing = light_sequence
        self.max_sequence_index = len(light_sequence.change_times)

    def update_playing_sequence(self):
        # TODO: this isnt very pretty
        change_time = self.sequence_playing.change_times[self.sequence_index]
        time_to_next_change = change_time + self.song_start_time - time.time()

        if time_to_next_change < 0:
            led_array = self.sequence_playing.led_array[self.sequence_index]
            self.__set_all_leds(led_array)
            self.pixels.show()

            self.sequence_index += 1
            if self.sequence_index >= self.max_sequence_index:
                # We have reached the end
                return 2
            return 1
        return 0

    def end_playing_sequence(self):
        self.song_start_time = 0
        self.sequence_index = 0
        self.sequence_playing = None
        self.max_sequence_index = 0

    def is_playing_sequence(self):
        return self.sequence_playing is not None

    def __set_all_leds(self, led_array):
        for i in range(self.N_LEDS):
            led_segment = math.floor(i/self.LEDS_PER_COLOUR)
            self.pixels[i] = led_array[led_segment]

    def turn_off_leds(self):
        self.__set_all_leds([(0, 0, 0)] * self.N_LEDS/self.LEDS_PER_COLOUR)
        self.pixels.show()

    def shutdown(self):
        self.turn_off_leds()
        self.pixels.deinit()


class PwmLedController:

    def __init__(self, red_pin=13, green_pin=19, blue_pin=26, pwm_freq=200):
        GPIO.setup(red_pin, GPIO.OUT)
        GPIO.setup(green_pin, GPIO.OUT)
        GPIO.setup(blue_pin, GPIO.OUT)

        self.red_pwm = GPIO.PWM(red_pin, pwm_freq)
        self.green_pwm = GPIO.PWM(green_pin, pwm_freq)
        self.blue_pwm = GPIO.PWM(blue_pin, pwm_freq)

        self.red_pwm.start(0)
        self.green_pwm.start(0)
        self.blue_pwm.start(0)

        self.MAX_CHANNEL = 100.0
        self.MIN_CHANNEL = 0.0

    def startup_pattern(self):
        """Light pattern to play at startup"""
        colours = np.array([[0,0,0], [255, 0, 0], [0, 255, 0], [0,0,255], [0,0,0]])
        interpolation_func = interp1d(np.arange(len(colours)) * 10, colours, axis=0)
        interpolated_colours = interpolation_func(np.arange((len(colours) - 1) * 10 + 1))
        interpolated_colours = self.__uint8_to_percentage(interpolated_colours)

        time_delay = 0.05
        for colour in interpolated_colours:
            self.__set_all_leds(colour)
            time.sleep(time_delay)

    def play_led_output(self, light_sequence, track_pos=0.0, break_function=None):
        start_time = time.time()
        for change_time, led_array in light_sequence:
            colour = self.__uint8_to_percentage(led_array)[0]

            time_to_next_change = change_time + start_time - track_pos - time.time()
            if time_to_next_change < 0:
                continue # If we are too late, skip to the next cycle
                # without sleeping or displaying

            time.sleep(time_to_next_change)
            self.__set_all_leds(colour)
            
            if break_function:
                if break_function():
                    return -1
                    
        return 0

    def __uint8_to_percentage(self, led_array):
        return np.clip(led_array.astype(float) * (100 / 255), 0.0, 100.0)

    def __set_all_leds(self, colour):
        self.red_pwm.ChangeDutyCycle(colour[0])
        self.green_pwm.ChangeDutyCycle(colour[1])
        self.blue_pwm.ChangeDutyCycle(colour[2])

    def shutdown(self):
        self.red_pwm.stop()
        self.green_pwm.stop()
        self.blue_pwm.stop()
        GPIO.cleanup()

