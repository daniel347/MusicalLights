import sounddevice as sd

import dsp
import light
import christmas_tree_sim as sim

DEV_ID = -1
BLOCK_DUR = 100  # by default, take 50ms chunks and feed them into the Fourier transform

light_freq_ranges = [(50, 200), (200, 300), (300, 400), (400, 650), (650, 1000)]
N_lights = len(light_freq_ranges)
MAX_FOURIER = 650  # TODO : dynamic gain adjustment - the required gain seems to vary a lot based on the music
lights = [light.Light(1, r, MAX_FOURIER, 0) for r in light_freq_ranges]  # make a light class instance for every frequency range
tree = sim.ChristmasTreeSim(N_lights)  # start the simulation of the tree

brightnesses = [10] * N_lights
update_display = False

def callback(indata, frames, time, status):
    """captures the audio at regular intervals and processes it as required"""
    global update_display

    if any(indata):
        fft, freqs = dsp.fourier(indata[:, 0], samplerate, gain=1000)
        # fft contains the fourier coefficients
        # freqs is an array of the corresponding frequencies

        bins = dsp.bin_spectrum(fft, freqs, light_freq_ranges)

        beat = dsp.detect_beat(indata[:, 0], 0.3)

        for light_obj, bin_val in zip(lights, bins):
            light_obj.set_brightness(bin_val, beat)  # saves data to light instance and also does scaling and constraining
            update_display = True

    else:
        print('no input', flush=True)


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
