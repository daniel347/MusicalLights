import sounddevice as sd
import numpy as np

import dsp
import light
import christmas_tree_sim as sim

DEV_ID = -1
BLOCK_DUR = 100  # by default, take 50ms chunks and feed them into the Fourier transform

light_freq_ranges = [(50, 200), (200, 300), (300, 400), (400, 650), (650, 1000)]
N_lights = len(light_freq_ranges)
MAX_FOURIER = 255  # TODO : unify gains into only the one adaptive one
lights = [light.Light(1, r, MAX_FOURIER, 0) for r in light_freq_ranges]  # make a light class instance for every frequency range
tree = sim.ChristmasTreeSim(N_lights)  # start the simulation of the tree

brightnesses = [10] * N_lights
update_display = False

audio_gain = 10
P_COEFF = 1
TARGET_LEVEL = 3
AUTOGAIN_T = 10  # time frame in seconds over which averages are taken for auto gain adjustment
sound_amplitudes = np.zeros(np.floor((AUTOGAIN_T * 1000) / BLOCK_DUR).astype(int))  # circular buffer of arrays

def callback(indata, frames, time, status):
    """captures the audio at regular intervals and processes it as required"""
    global update_display

    if any(indata):
        amplified_audio = np.array(indata[:, 0]) * audio_gain
        fft, freqs = dsp.fourier(amplified_audio, samplerate)
        # fft contains the fourier coefficients
        # freqs is an array of the corresponding frequencies

        bins = dsp.bin_spectrum(fft, freqs, light_freq_ranges)

        beat = dsp.detect_beat(amplified_audio, 0.3)
        update_gain(dsp.rms(amplified_audio))

        for light_obj, bin_val in zip(lights, bins):
            light_obj.set_brightness(bin_val, beat)  # saves data to light instance and also does scaling and constraining
            update_display = True

    else:
        print('no input', flush=True)

def update_gain(rms_amplitude):
    """function for adaptive audio gain"""
    global audio_gain

    # first add the new amplitude to the circular buffer
    sound_amplitudes[0] = rms_amplitude
    np.roll(sound_amplitudes, 1)

    audio_gain += (TARGET_LEVEL - dsp.rms(sound_amplitudes)) * P_COEFF


if __name__ == "__main__":

    if (DEV_ID < 0):
        DEV_ID = sd.default.device["input"]
        print(DEV_ID)

    samplerate = sd.query_devices(DEV_ID)['default_samplerate']
    blocksize = int((samplerate * BLOCK_DUR) / 1000)

    tree.draw_tree(brightnesses)

    with sd.InputStream(device=DEV_ID, channels=1, callback=callback, blocksize=blocksize, samplerate=samplerate):
        while True:
            if update_display:
                brightnesses = [l.brightness for l in lights]
                tree.draw_tree(brightnesses)
                update_display = False
