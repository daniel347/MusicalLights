import time

import sounddevice as sd
import numpy as np
import cProfile
from tkinter import *
from tkinter.ttk import *

import dsp
import light
import christmas_tree_sim as sim

# ========PROFILING========
pr = cProfile.Profile()
pr.disable()
# =========================

# ========LIGHTS========
N_lights = 5
MODE = light.Mode.freq_range  # options are in the Enum class within light.py

# frequency range options
light_freq_ranges = [(50, 200), (200, 300), (300, 400), (400, 650), (650, 1000)]
assert (len(light_freq_ranges) == N_lights)
MAX_FOURIER = 255
LOW_THRESH = 5
DECAY_RATE = 350
INCREASE_RATE = 2000
update_lights = True
BEAT_INCREASE = 0

# loudness mode options
loudness_levels = [0.5, 1, 3, 5, 7]
LOUDNESS_GRADIENT = 255
assert (len(loudness_levels) == N_lights)

# This list defines the hardware configuration of lights and how they should react to the sound.
# see light class for options and parameters.
lights = [light.Light(1, MODE, LOW_THRESH, DECAY_RATE, INCREASE_RATE) for i in range(N_lights)]

for l, r in zip(lights, light_freq_ranges):
    l.setup_freq_range_mode(r, MAX_FOURIER, BEAT_INCREASE)

for l, v in zip(lights, loudness_levels):
    l.setup_loudness_mode(v, LOUDNESS_GRADIENT)
# ======================

# ========SIMULATION========
SIMULATE = True
brightnesses = [10] * N_lights
if SIMULATE:
    tree = sim.ChristmasTreeSim(N_lights)  # start the simulation of the tree

UPDATE_PERIOD = 25  # time between successive frames in ms
# ==========================


# ========AUDIO PARAMETERS========
DEV_ID = -1
BLOCK_DUR = 100  # by default, take 50ms chunks and feed them into the Fourier transform

audio_gain = 300
P_COEFF = 0.1
TARGET_LEVEL = 20
AUTOGAIN_T = 10  # time frame in seconds over which averages are taken for auto gain adjustment
sound_amplitudes = np.zeros(np.floor((AUTOGAIN_T * 1000) / BLOCK_DUR).astype(int))  # circular buffer of arrays
# ================================

stop_callback = False

class GUI:

    def __init__(self, window):

        # Lighting mode
        self.mode_label = Label(window, text="Mode")
        self.mode_label.grid(column=1, row=0)

        self.mode_dropdown = Combobox(window)
        self.mode_dropdown_options = ("Frequency Range", "Loudness")
        self.mode_dropdown['values'] = self.mode_dropdown_options
        self.mode_dropdown.current(0)
        self.mode_dropdown.grid(column=1, row=1)

        # Frequency ranges
        self.freq_range_title = Label(window, text="Light Frequency Ranges", font=("Helvetica", 16))
        self.freq_range_title.grid(column=1, row=2)

        self.light_freq_guis = []
        self.light_freq_vars = []
        for i, range in enumerate(light_freq_ranges):
            low_var = IntVar().set(range[0])
            low_range = Spinbox(window, from_=0, to=2000, width=10, textvariable=low_var)
            low_range.set(range[0])
            low_range.grid(column=0, row=(3 + i), sticky=E)

            light_name = Label(window, text=("Light " + str(i)))
            light_name.grid(column=1, row=(3 + i))

            high_var = IntVar().set(range[1])
            high_range = Spinbox(window, from_=0, to=2000, width=10, textvariable=high_var)
            high_range.set(range[1])
            high_range.grid(column=2, row=(3 + i), sticky=W)

            self.light_freq_guis.append((light_name, low_range, high_range))
            self.light_freq_vars.append((low_var, high_var))

        # Loudness values
        self.loudness_title = Label(window, text="Loudness Cut-offs", font=("Helvetica", 16))
        self.loudness_title.grid(column=1, row=4 + N_lights)

        self.light_loudness_guis = []
        self.light_loudness_vars = []
        for i, loudness in enumerate(loudness_levels):
            light_name = Label(window, text=("Light " + str(i)))
            light_name.grid(column=0, row=(6 + N_lights + i))

            loudness_var = DoubleVar().set(loudness)
            l = Scale(window, orient=HORIZONTAL, length=100, from_=0.0, to=20.0, variable=loudness_var)
            l.set(loudness)
            l.grid(column=1, row=(6 + N_lights + i))

            self.light_loudness_vars.append(loudness_var)
            self.light_loudness_guis.append((light_name, l))

        self.light_param_title = Label(window, text="Other Light Parameters", font=("Helvetica", 16))
        self.loudness_title.grid(column=1, row=7 + 2*N_lights)

        # Low threshold
        self.low_thresh_label = Label(window, text="Light Low Threshold ")
        self.low_thresh_label.grid(column=0, row=(9 + 2*N_lights))

        self.low_thresh_var = IntVar().set(LOW_THRESH)
        self.low_thresh = Spinbox(window, from_=0, to=255, width=10, textvariable=self.low_thresh_var)
        self.low_thresh.set(LOW_THRESH)
        self.low_thresh.grid(column=1, row=(9 + 2*N_lights))

        # Decay rate
        self.decay_rate_label = Label(window, text="Light Decay Rate")
        self.decay_rate_label.grid(column=0, row=(10 + 2 * N_lights))

        self.decay_rate_var = IntVar().set(LOW_THRESH)
        self.decay_rate = Spinbox(window, from_=0, to=500, width=10, textvariable=self.decay_rate_var)
        self.decay_rate.set(DECAY_RATE)
        self.decay_rate.grid(column=1, row=(10 + 2 * N_lights))

        # Increase rate
        self.increase_rate_label = Label(window, text="Light increase Rate")
        self.increase_rate_label.grid(column=0, row=(10 + 2 * N_lights))

        self.increase_rate_var = IntVar().set(LOW_THRESH)
        self.increase_rate = Spinbox(window, from_=0, to=255, width=10, textvariable=self.increase_rate_var)
        self.increase_rate.set(DECAY_RATE)
        self.increase_rate.grid(column=1, row=(10 + 2 * N_lights))

        # Beat increase
        self.beat_increase_label = Label(window, text="Increase Brightness on Beat")
        self.beat_increase_label.grid(column=0, row=(11 + 2 * N_lights))

        self.beat_increase_var = IntVar().set(LOW_THRESH)
        self.beat_increase = Spinbox(window, from_=0, to=255, width=10, textvariable=self.beat_increase_var)
        self.beat_increase.set(BEAT_INCREASE)
        self.beat_increase.grid(column=1, row=(11 + 2 * N_lights))

        # Audio Level
        self.audio_level_label = Label(window, text="Target Audio Level")
        self.audio_level_label.grid(column=0, row=(12 + 2 * N_lights))

        self.audio_level_var = DoubleVar().set(TARGET_LEVEL)
        self.audio_level = Scale(window, orient=HORIZONTAL, length=200, from_=0.0, to=100.0, variable=self.audio_level_var)
        self.audio_level.set(TARGET_LEVEL)
        self.audio_level.grid(column=1, row=(12 + 2*N_lights))

        # update button
        self.update_button = Button(window, text="Update Parameters", width=50, command=self.update_parameters)
        self.update_button.grid(column=1, row=13 + 2 * N_lights)

    def update_parameters(self):
        print("Button pressed")
        global MODE, TARGET_LEVEL

        # update mode
        for i, mode in enumerate(self.mode_dropdown_options):
            if (self.mode_dropdown.get() == mode):
                MODE = light.Mode(i + 1)  # NB : enum list and dropdown list must be in the same order

        # setup lights with new variables
        for l, (_, low_var, high_var), (_, loudness) in zip(lights, self.light_freq_guis, self.light_loudness_guis):
            # frequency mode setup
            l.setup_freq_range_mode((int(low_var.get()), int(high_var.get())), MAX_FOURIER, self.beat_increase.get())

            # loudness mode setup
            l.setup_loudness_mode(loudness.get(), LOUDNESS_GRADIENT)

            # mode, decay, increase rates and low thresh
            l.mode = MODE
            l.DECAY_RATE = int(self.decay_rate.get())
            l.LOW_THRESH = int(self.low_thresh.get())
            l.INCREASE_RATE = int(self.increase_rate.get())

        # audio parameters
        TARGET_LEVEL = self.audio_level.get()


def callback(indata, frames, time, status):
    """captures the audio at regular intervals and processes it as required"""
    global update_lights

    if stop_callback:
        raise sd.CallbackStop()  # ends the callback when the main loop finishes

    if any(indata):
        # first amplify the audio and adjust the gain
        amplified_audio = np.array(indata[:, 0]) * audio_gain
        update_gain(dsp.rms(amplified_audio))

        fft, freqs = dsp.fourier(amplified_audio, samplerate)
        # fft contains the fourier coefficients
        # freqs is an array of the corresponding frequencies

        for light_obj in lights:
            # calculate the brightness of each light instance from the sound
            light_obj.set_brightness(fourier=fft, freqs=freqs, loudness=sound_amplitudes[1])

        update_lights = True

    else:
        print('no input', flush=True)


def update_gain(rms_amplitude):
    """function for adaptive audio gain"""
    global audio_gain
    global sound_amplitudes

    # first add the new amplitude to the circular buffer
    sound_amplitudes[0] = rms_amplitude
    sound_amplitudes = np.roll(sound_amplitudes, 1)

    print(rms_amplitude)

    audio_gain += (TARGET_LEVEL - dsp.rms(sound_amplitudes)) * P_COEFF

def main_loop(window, dt):
    brightnesses = [l.decay_grow(dt) for l in lights]

    if SIMULATE:  # if running the simulation, update this
        tree.draw_tree(brightnesses)
    window.after(dt, main_loop, window, dt)


if __name__ == "__main__":

    # ========GUI========
    window = Tk()
    window.title("Musical Lights")
    window.geometry('600x500')

    gui = GUI(window)
    # ===================

    # ========AUDIO PARAMETERS========
    if (DEV_ID < 0):
        DEV_ID = sd.default.device["input"]

    samplerate = sd.query_devices(DEV_ID)['default_samplerate']
    blocksize = int((samplerate * BLOCK_DUR) / 1000)
    # ================================

    if SIMULATE:
        tree.draw_tree(brightnesses)

    # ========MAIN LOOP========
    with sd.InputStream(device=DEV_ID, channels=1, callback=callback, blocksize=blocksize, samplerate=samplerate):
        window.after(UPDATE_PERIOD, main_loop, window, UPDATE_PERIOD)
        window.mainloop()
    # =========================


