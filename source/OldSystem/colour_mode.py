import enum


class ColourMode(enum.Enum):
    spectrum = 1
    single_colour = 2
    alternating_two = 3  # every other LED is the same colour
    change_on_beat = 4