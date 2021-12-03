import numpy as np
import math
from light_sequence import LightSequence
from scipy.interpolate import interp1d
from Enumerations import colour_schemes

class Colours:
    def __init__(self, N_LEDS, MIN_CHANNEL, MAX_CHANNEL):
        self.N_LEDS = N_LEDS

        self.MAX_CHANNEL = MAX_CHANNEL
        self.MIN_CHANNEL = MIN_CHANNEL

        self.colour_schemes = colour_schemes


        self.colour_functions = ["colour_change_on_beat",
                                 "colour_fade_on_beat",
                                 "colour_pulse_on_beat"]
        # All these have the same interface

        self.colour_sub_sequences = ["colour_change_increasing_frequency"]

    def colour_change_on_beat(self, colour_list, beats, duration_shift=0.0, subdivide=1):
        """Best with clear defined beats/bars and faster tempo"""
        if type(colour_list) == str:
            colour_list = self.colour_schemes[colour_list]

        num_colours = len(colour_list)

        colour_sequence = np.repeat(colour_list, self.N_LEDS, axis=0)\
            .reshape((num_colours, self.N_LEDS, 3))

        num_whole_cycles = math.floor((len(beats) * subdivide)/num_colours)
        remainder_beats = (len(beats) * subdivide) % num_colours
        full_sequence = np.concatenate([np.tile(colour_sequence, (num_whole_cycles, 1, 1)),
                                  colour_sequence[:remainder_beats, :, :]], axis=0)

        change_times = np.array([beat["start"] + beat["duration"] * duration_shift
                                 for beat in beats])
        if subdivide > 1:
            change_times = np.interp(np.arange(len(full_sequence)),
                                     np.arange(len(beats)) * subdivide,
                                     change_times)

        return LightSequence(full_sequence, change_times)

    def colour_fade_on_beat(self, colour_list, beats, interpolated_points=20, duration_shift=0):
        """Best with slow to medium tempos and less defined beats"""
        if type(colour_list) == str:
            colour_list = self.colour_schemes[colour_list]

        unfaded_sequence = self.colour_change_on_beat(colour_list, beats, duration_shift)
        change_times = unfaded_sequence.change_times
        full_sequence = unfaded_sequence.led_array

        interpolation_func = interp1d(change_times, full_sequence, axis=0)
        interpolated_times = np.interp(np.arange(len(beats) * interpolated_points),  # 0,1,2,3,4
                                       np.arange(len(beats)) * interpolated_points,  # 0, 5
                                       change_times)
        interpolated_sequence = interpolation_func(interpolated_times)

        return LightSequence(interpolated_sequence, interpolated_times)

    def colour_pulse_on_beat(self, colour_list, beats, duration_shift=0, fill_colour=np.array([0,0,0])):
        """Best with a sharp emphasis on beats/bars and fast tempo"""
        if type(colour_list) == str:
            colour_list = self.colour_schemes[colour_list]

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

    def modulate_brightness_on_loudness(self, light_sequence, segments, interpolated_points=20, duration_offset=0):
        """Best used with a single colour for regions with large loudness variations/silent periods"""
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

    def colour_change_increasing_frequency(self, colour_list, analysis, section_num, duration_shift=0.8, time_ratio=[0.33, 0.66, 1]):
        """Rave-like a useful buildup for somewhat fast paced songs or before bass drops"""
        slow_pace = self.colour_change_on_beat(colour_list, analysis["bars"], duration_shift)
        medium_pace = self.colour_change_on_beat(colour_list, analysis["tatums"], duration_shift)
        fast_pace = self.colour_change_on_beat(colour_list, analysis["tatums"], duration_shift, subdivide=4)

        section = analysis["sections"][section_num]
        change_times = np.array([0,
                                section["duration"] * time_ratio[0],
                                section["duration"] * time_ratio[1],
                                section["duration"] * time_ratio[2]])
        change_times += section["start"]

        return LightSequence(sequence_list_time=[slow_pace, medium_pace, fast_pace],
                            switch_times=change_times)

    def choose_colour_schemes_for_time_signature(self, time_signature):
        possible_colours = []
        for arr in self.colour_schemes.values():
            if len(arr) % time_signature == 0 or time_signature % len(arr) == 0:
                possible_colours.append(arr)

        return possible_colours

    def make_uniform_colour_array(self, colour):
        return np.array([colour] * self.N_LEDS)











