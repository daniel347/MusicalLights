import numpy as np


def fourier(data, samplerate, gain=1000):
    """Computes the fourier transform for a given input"""

    fft = np.abs(np.fft.rfft(data, norm="ortho")) * gain
    frequencies = np.fft.rfftfreq(len(data), 1.0 / samplerate)

    return fft, frequencies


def bin_spectrum(fourier, freqs, freq_ranges):
    """Method of grouping output of Fourier into bins, each bin defined by a tuple containing min and max frequencies
    The tuples are passed in a list freq_range
    """
    num_bins = len(freq_ranges)
    binned_spectrum = [0] * num_bins

    for light_index, range in enumerate(freq_ranges):
        num_freq_in_light = 0

        for fft, f in zip(fourier, freqs):
            if range[0] <= f < range[1]:  # this frequency is in the range corresponding to one of the lights
                binned_spectrum[light_index] += fft
                num_freq_in_light += 1
            if f > range[1]:  # we have passed the range therefore no need to look any further
                break

        binned_spectrum[light_index] /= num_freq_in_light  # divide by number of values to obtain a mean

    return binned_spectrum


def detect_beat(audio, change_thresh):
    """"Detects the beat as an increase in volume. change_tresh indicated the increase neccessary as a multiple of the
    rms volume"""
    SPLIT = 2
    N = len(audio)
    sec_len = N / SPLIT  # length of sections to take an RMS mean over

    # calculate RMS mean (volume level) over sub intervals of the sample
    rms_means = [0] * SPLIT
    for n in range(SPLIT):
        rms_means[n] = np.sum(np.square(audio[int(sec_len * n):int(sec_len * (n + 1))]))

    rms_differences = [(rms_means[i] - rms_means[i - 1]) for i in range(1, SPLIT)]
    total_mean = np.sum(rms_means) / SPLIT

    if max(rms_differences) >= total_mean * change_thresh:
        return True
    else:
        return False
