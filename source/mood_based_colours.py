from enum import Enum

class MoodBasedColours():

    def __init__(self, thresholds):
        self.thresholds = thresholds

    def classify_music(self, features):
        key = None
        if features["key"] != -1:
            key = Key(features["key"])

        major = bool(section["mode"]) if section["mode"] != -1 else None
        time_signature = features["time_signature"] > self.thresholds["danceability"]
        danceable = features["danceability"] > self.thresholds["danceability"]
        energetic = features["energy"] > self.thresholds["energy"]
        high_valence = features["valence"] > self.thresholds["valence"]
        tempo = features["tempo"] > self.thresholds["tempo"]

    def choose_modes_from_sections(self, anaysis):
        for section in anaysis["sections"]:
            key = None
            if section["key"] != -1:
                key = Key(section["key"])

            major = bool(section["mode"]) if section["mode"] != -1 else None


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