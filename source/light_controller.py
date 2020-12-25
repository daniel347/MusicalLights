import neopixel
import board
import time
import RPi.GPIO as GPIO
import numpy as np
from scipy.interpolate import interp1d

class LightController():

    def __init__(self, N_LEDS):
        self.N_LEDS = N_LEDS
        self.pixels = neopixel.NeoPixel(board.D18, N_LEDS, auto_write=False)

        self.MAX_CHANNEL = 255
        self.MIN_CHANNEL = 0
        
    def startup_pattern(self):
        """"Light pattern to play at startup"""
        start_pattern = [(50, 0, 0), (75, 100, 0), (0, 255, 0), (0, 100, 75),
                         (0, 0, 50)]  # like a small spectrum wave

        speed = 0.01  # time delay between moving the wave up one pixel

        for wave_pos in range(self.N_LEDS - len(start_pattern)):
            self.pixels.fill((0, 0, 0))
            for i, c in enumerate(start_pattern):
                self.pixels[wave_pos + i] = c

            self.pixels.show()
            time.sleep(speed)

    def play_led_output(self, light_sequence, track_pos=0.0):
        start_time = time.time()
        for change_time, led_array in light_sequence:
            self.__set_all_leds(led_array)

            time_to_next_change = change_time + start_time - track_pos - time.time()
            if time_to_next_change < 0:
                continue # If we are too late, skip to the next cycle
                # without sleeping or displaying

            time.sleep(time_to_next_change)
            self.pixels.show()

    def __set_all_leds(self, led_array):
        for i in range(self.N_LEDS):
            self.pixels[i] = led_array[i]

    def shutdown(self):
        self.__set_all_leds([(0, 0, 0)] * self.N_LEDS)
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

