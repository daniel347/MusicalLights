
class Light:

    def __init__(self, pin, freq_range, max_fourier, beat_inc):
        # light parameters
        self.brightness = 0
        self.MAX_BRIGHTNESS = 255
        self.MIN_BRIGHTNESS = 0
        self.LOW_THRESH = 25  # discount low levels of noise in the signal by keeping the lights off if under this value
        self.DECAY_RATE = 25  # slowly fades out lights to prolong the effect
        self.gpio_pin = pin


        # Frequency range based brightness varying
        # controls the scale factor to convert the fourier bins to brightness levels
        self.fourier_scale = self.MAX_BRIGHTNESS / max_fourier
        self.freq_range = freq_range

        # Beat based flashing
        self.beat_increment = beat_inc  # the value to increase brightness temporarily on the beat

    def set_brightness(self, fourier_bin, beat):
        """"Sets a new brightness for the light, based on the parameters set up in init and the audio input
        For decay, it is assumed that set_brightness is called at regular intervals"""
        # frequency based brightness variation
        b = fourier_bin * self.fourier_scale

        # beat based flashing
        if beat:
            b += self.beat_increment

        # constrain to light minimum and maximum
        b = min(self.MAX_BRIGHTNESS, max(self.MIN_BRIGHTNESS, b))

        # if the light decrease is greater than the max decay rate, reduce the brightness slowly
        if self.brightness - b > self.DECAY_RATE:
            b = self.brightness - self.DECAY_RATE

        # if the light brightness is lower than thresh, turn off fully to avoid a strange "slightly glowing" look
        if b <= self.LOW_THRESH:
            b = 0

        self.brightness = int(round(b))

    def out_pwm(self):
        """"Ouput a pwm to the GPIO pin to control the light"""
        pass

    def fourier_brightness_component(self, fourier, freqs):
        """Calculates the power over the frequency range of the light"""

        freq_power = 0  # power over the frequency range of the light
        num_freq = 0  # number of frequencies used in mean

        for fft, f in zip(fourier, freqs):
            if self.freq_range[0] <= f < self.freq_range[1]:  # this frequency is in the range of this light
                freq_power += fft
                num_freq += 1
            if f > self.freq_range[1]:  # we have passed the range therefore no need to look any further
                break

        return int(round((freq_power/num_freq) * self.fourier_scale))

    def loudness_brightness_component(self, loudness):


    # TODO : add in multiple modes - eg one shwoing loudness as height in the tree
