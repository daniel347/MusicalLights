import enum


class Light:

    def __init__(self, pin, mode, low_thresh, decay_rate):
        # light parameters
        self.brightness = 0
        self.MAX_BRIGHTNESS = 255
        self.MIN_BRIGHTNESS = 0
        self.LOW_THRESH = low_thresh  # discount low levels of noise in the signal by keeping the lights off if under this value
        self.DECAY_RATE = decay_rate  # slowly fades out lights to prolong the effect
        self.gpio_pin = pin

        # mode control enum - NB: main must run the appropriate setup function after init
        self.mode = mode
        print(self.mode)

    def setup_freq_range_mode(self, freq_range, max_fourier, beat_inc):
        """set parameters for frequency range mode operation"""
        # controls the scale factor to convert the fourier bins to brightness levels
        self.fourier_scale = self.MAX_BRIGHTNESS / max_fourier
        self.freq_range = freq_range

        # Beat based flashing
        self.beat_increment = beat_inc  # the value to increase brightness temporarily on the beat

    def setup_loudness_mode(self, min_loudness, loudness_gradient):
        """set parameters for loudness mode operation. In this mode the light activates at a particular volume"""
        # brightness = LOUDNESS_GRAD * (loudness - MIN_LOUDNESS)
        self.MIN_LOUDNESS = min_loudness
        self.LOUDNESS_GRAD = loudness_gradient

    def set_brightness(self, fourier=None, freqs=None, beat=False, loudness=None):
        """"Sets a new brightness for the light, based on the parameters set up in init and the audio input
        For decay, it is assumed that set_brightness is called at regular intervals"""
        b = 0

        if (self.mode == Mode.freq_range):
            if fourier is None or freqs is None:
                return  # if no data is supplied make no change to brightness
            b = self.fourier_brightness_component(fourier, freqs)
        elif (self.mode == Mode.loudness):
            if loudness is None:
                return  # if no data is supplied make no change to brightness
            b = self.loudness_brightness_component(loudness)

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
        """Calculates the brightness due to power over the frequency range of the light"""

        freq_power = 0  # power over the frequency range of the light
        num_freq = 0  # number of frequencies used in mean

        for fft, f in zip(fourier, freqs):
            if self.freq_range[0] <= f < self.freq_range[1]:  # this frequency is in the range of this light
                freq_power += fft
                num_freq += 1
            if f > self.freq_range[1]:  # we have passed the range therefore no need to look any further
                break

        return int(round((freq_power / num_freq) * self.fourier_scale))

    def loudness_brightness_component(self, loudness):
        """Calculates the brightness for loudness mode"""

        if (loudness < self.MIN_LOUDNESS):
            return 0
        else:
            return int(round(self.LOUDNESS_GRAD * (loudness - self.MIN_LOUDNESS)))


class Mode(enum.Enum):
    freq_range = 1
    loudness = 2
