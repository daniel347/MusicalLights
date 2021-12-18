import enum
import numpy as np

class LightingModes(enum.Enum):
    Static = 0
    Sequence = 1
    MusicReactive = 2

class LightSequences(enum.Enum):
    RedGreenBlue = 0
    YellowSomething = 1

colour_schemes = {
    "Rave": np.array([[255, 0, 0], [0, 255, 0], [0, 255, 255], [255, 0, 255], [0, 0, 255], [255, 255, 0]]),

    "Pastel1": np.array([[118, 227, 185], [252, 255, 74], [217, 78, 78], [225, 154, 245], [116, 190, 232]]),

    "Pastel2": np.array([[116, 232, 90], [255, 182, 143], [98, 94, 214], [52, 55, 194]]),
    "Neon1": np.array([[0, 255, 255], [250, 255, 0], [255, 100, 0], [255, 0, 255]]),

    "RedGreenBlue": np.array([[255, 42, 0], [0, 255, 128], [0, 51, 255]]),
    "Neon2": np.array([[111, 255, 0], [200, 0, 255], [0, 150, 255]]),

    "Warning": np.array([[255, 42, 0], [255, 255, 255]]),
    "GreenWhite": np.array([[128, 255, 0], [255, 255, 255]]),
    "BlueWhite": np.array([[0, 51, 255], [255, 255, 255]])
}

colour_functions = ["colour_change_on_beat",
                    "colour_fade_on_beat",
                    "colour_pulse_on_beat"]