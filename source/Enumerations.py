import enum

class LightingModes(enum.Enum):
    Static = 0
    Sequence = 1
    MusicReactive = 2

class LightSequences(enum.Enum):
    RedGreenBlue = 0
    YellowSomething = 1