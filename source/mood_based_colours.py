from enum import Enum
import random
from light_sequence import LightSequence

class MoodBasedColours():

    def __init__(self, thresholds):
        self.thresholds = thresholds

    def classify_music(self, features):
        key = None
        if features["key"] != -1:
            key = Key(features["key"])

        major = bool(features["mode"]) if features["mode"] != -1 else None
        time_signature = features["time_signature"]
        danceable = features["danceability"] > self.thresholds["danceability"]
        energetic = features["energy"] > self.thresholds["energy"]
        high_valence = features["valence"] > self.thresholds["valence"]
        tempo = features["tempo"]

        return AudioFeatures(key, major, time_signature, danceable,
                             energetic, high_valence, tempo)

    def choose_track_lighting(self, colours, audio_features, analysis):

        possible_colour_schemes = colours.choose_colour_schemes_for_time_signature(
                                            audio_features.time_signature)
        colour_scheme = random.choice(possible_colour_schemes)

        led_sections = []
        section_times = []
        completed_sub_sequences = []

        for sec_num, section in enumerate(analysis["sections"]):
            section_times.append(section["start"])

            # for colour schemes that are very short add more variety
            if colour_scheme.shape[0] <= 2:
                colour_scheme = random.choice(possible_colour_schemes)

            # for sections of the right length use the subsequences
            if 20 > section["duration"] > 5:
                sub_sequence = random.choice(colours.colour_sub_sequences)
                if random.randint(1, 3) == 1 and sub_sequence not in completed_sub_sequences:
                    completed_sub_sequences.append(sub_sequence)
                    led_section = getattr(colours, sub_sequence)(colour_scheme, analysis, sec_num)
                    led_sections.append(led_section)
                    continue

            # otherwise chose from the normal functions
            mode = random.choice(colours.colour_functions)
            speed = random.choice(["bars", "beats", "tatums"])
            led_sections.append(getattr(colours, mode)(colour_scheme, analysis[speed]))

        # append the final section end
        section_times.append(section["start"] + section["duration"])
        return LightSequence(sequence_list_time=led_sections,
                                 switch_times=section_times)


class AudioFeatures:

    def __init__(self,
                 key,
                 major,
                 time_signature,
                 danceable,
                 energetic,
                 high_valence,
                 tempo):

        self.key = key
        self.major = major
        self.time_signature = time_signature
        self.danceable = danceable
        self.energetic = energetic
        self.high_valence = high_valence
        self.tempo = tempo


class Key(Enum):
    C = 0
    C_SHARP = 1
    D = 2
    D_SHARP = 3
    E = 4
    F = 5
    F_SHARP = 6
    G = 7
    G_SHARP = 8
    A = 9
    A_SHARP = 10
    B = 11