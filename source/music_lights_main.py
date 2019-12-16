import sounddevice as sd
import numpy as np
import cProfile

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
assert(len(light_freq_ranges) == N_lights)
MAX_FOURIER = 255
LOW_THRESH = 25
DECAY_RATE = 25
update_lights = False
BEAT_INCREASE = 0

# loudness mode options
loudness_levels = [0.5, 1, 3, 5, 7]
LOUDNESS_GRADIENT = 255
assert(len(loudness_levels) == N_lights)

# This list defines the hardware configuration of lights and how they should react to the sound.
# see light class for options and parameters.
lights = [light.Light(1, MODE, LOW_THRESH, DECAY_RATE) for i in range(N_lights)]

if MODE == light.Mode.freq_range:
    for l, r in zip(lights, light_freq_ranges):
        l.setup_freq_range_mode(r, MAX_FOURIER, BEAT_INCREASE)

elif MODE == light.Mode.loudness:
    for l, v in zip(lights, loudness_levels):
        l.setup_loudness_mode(v, LOUDNESS_GRADIENT)
# ======================

# ========SIMULATION========
SIMULATE = True
brightnesses = [10] * N_lights
if SIMULATE:
    tree = sim.ChristmasTreeSim(N_lights)  # start the simulation of the tree
# ==========================


# ========AUDIO PARAMETERS========
DEV_ID = -1
BLOCK_DUR = 100  # by default, take 50ms chunks and feed them into the Fourier transform

audio_gain = 100
P_COEFF = 1
TARGET_LEVEL = 20
AUTOGAIN_T = 10  # time frame in seconds over which averages are taken for auto gain adjustment
sound_amplitudes = np.zeros(np.floor((AUTOGAIN_T * 1000) / BLOCK_DUR).astype(int))  # circular buffer of arrays
# ================================

stop_callback = False

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


if __name__ == "__main__":

    # /////////////////////////////////
    # Set up audio recording parameters
    if (DEV_ID < 0):
        DEV_ID = sd.default.device["input"]

    samplerate = sd.query_devices(DEV_ID)['default_samplerate']
    blocksize = int((samplerate * BLOCK_DUR) / 1000)
    # /////////////////////////////////

    if SIMULATE:
        tree.draw_tree(brightnesses)

    # ========MAIN LOOP========
    with sd.InputStream(device=DEV_ID, channels=1, callback=callback, blocksize=blocksize, samplerate=samplerate):
        while True:
            if update_lights:
                # update the light brightnesses now

                if SIMULATE:  # if running the simulation, update this
                    brightnesses = [l.brightness for l in lights]
                    tree.draw_tree(brightnesses)
                update_lights = False

                # some method of killing the system - maybe tkinter gui for actual useage
    # =========================

