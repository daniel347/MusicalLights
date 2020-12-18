import numpy as np
import math
from light_sequence import LightSequence
from scipy.interpolate import interp1d

class Colours:
    def __init__(self, N_LEDS, MIN_CHANNEL, MAX_CHANNEL):
        self.N_LEDS = N_LEDS

        self.MAX_CHANNEL = MAX_CHANNEL
        self.MIN_CHANNEL = MIN_CHANNEL

    def colour_change_on_beat(self, colour_list, beats, duration_shift=0):
        num_colours = len(colour_list)

        colour_sequence = np.repeat(colour_list, self.N_LEDS, axis=0)\
            .reshape((num_colours, self.N_LEDS, 3))

        num_whole_cycles = math.floor(len(beats)/num_colours)
        remainder_beats = len(beats) % num_colours
        full_sequence = np.concatenate([np.tile(colour_sequence, (num_whole_cycles, 1, 1)),
                                  colour_sequence[:remainder_beats, :, :]], axis=0)

        change_times = np.array([beat["start"] + beat["duration"] * duration_shift
                                 for beat in beats])

        return LightSequence(full_sequence, change_times)

    def colour_fade_on_beat(self, colour_list, beats, interpolated_points=5, duration_shift=0):
        unfaded_sequence = self.colour_change_on_beat(colour_list, beats, duration_shift)
        change_times = unfaded_sequence.change_times
        full_sequence = unfaded_sequence.led_array

        interpolation_func = interp1d(change_times, full_sequence, axis=0)
        interpolated_times = np.interp(np.arange(len(beats) * interpolated_points),  # 0,1,2,3,4
                                       np.arange(len(beats)) * interpolated_points,  # 0, 5
                                       change_times)
        interpolated_sequence = interpolation_func(interpolated_times)

        return LightSequence(interpolated_sequence, interpolated_times)

    def colour_pulse_on_beat(self, colour_list, fill_colour, beats, duration_shift=0):
        filled_colour_list = list(colour_list)
        for i in range(len(colour_list)-1, -1, -1):
            filled_colour_list.insert(i, fill_colour)

        num_colours = len(filled_colour_list)
        filled_colour_list = np.array(filled_colour_list)

        colour_sequence = np.repeat(filled_colour_list, self.N_LEDS, axis=0) \
                            .reshape((num_colours, self.N_LEDS, 3))

        num_whole_cycles = math.floor(len(beats)/num_colours)
        remainder_beats = len(beats) % num_colours
        full_sequence = np.concatenate([np.tile(colour_sequence, (num_whole_cycles, 1, 1)),
                                        colour_sequence[:remainder_beats, :, :]], axis=0)

        change_times = []
        for beat in beats:
            change_times.append(beat["start"] + beat["duration"] * duration_shift)
            change_times.append(beat["start"] + beat["duration"] * (1 + duration_shift))

        change_times = np.array([beat["start"] + beat["duration"] * duration_shift
                                 for beat in beats])

        return LightSequence(full_sequence, change_times)

    def modulate_brightness_on_loudness(self, light_sequence, segments, interpolated_points=5, duration_offset=0):
        loudness_times = np.array([segment["start"] + segment["duration"] * duration_offset
                                   for segment in segments])
        loudness_values = np.array([segment["loudness_max"] for segment in segments])
        global_max_loudness = loudness_values.max()
        global_min_loudness = loudness_values.min()

        interpolated_times = np.interp(np.arange(len(light_sequence.change_times) * interpolated_points),  # 0,1,2,3,4
                                       np.arange(len(light_sequence.change_times)) * interpolated_points,  # 0, 5
                                       light_sequence.change_times)
        interpolated_brightness = (np.interp(interpolated_times, loudness_times, loudness_values) - global_min_loudness)/(global_max_loudness - global_min_loudness)

        modulated_led_array = np.repeat(light_sequence.led_array,
                                        interpolated_points,
                                        axis=0)

        modulated_led_array = np.clip((modulated_led_array * interpolated_brightness[:, None, None]).astype(np.uint8),
                                    self.MIN_CHANNEL, self.MAX_CHANNEL)

        return LightSequence(modulated_led_array, interpolated_times)




