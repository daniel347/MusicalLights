import numpy as np
import math

def fourier(data, samplerate):
    """Computes the fourier transform for a given input"""

    fft = np.abs(np.fft.rfft(data, norm="ortho"))
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
        rms_means[n] = rms(audio[int(sec_len * n):int(sec_len * (n + 1))])

    rms_differences = [(rms_means[i] - rms_means[i - 1]) for i in range(1, SPLIT)]
    total_mean = np.sum(rms_means) / SPLIT

    if max(rms_differences) >= total_mean * change_thresh:
        return True
    else:
        return False

def detect_beat_long(buffer, change_thresh, min_vol):
    """"Alternative beat detection based on finding a mnaximum over a longer timespan
    Aslo supresses the many successive beats which are detected in slience"""
    RANGE = 10  # go back ten samples
    if len(buffer) > RANGE:
        RANGE = len(buffer)

    rms_over_range = rms(buffer[1:RANGE])

    if buffer[0] >= rms_over_range * change_thresh and buffer[0] > min_vol:
        return True
    else:
        return False

def rms(arr):
    """calculates the RMS mean of the numpy array arr"""
    return math.sqrt(np.sum(np.square(arr))/len(arr))