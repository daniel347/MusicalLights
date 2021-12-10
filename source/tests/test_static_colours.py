import time
import os

from colour_modes import Colours
import math

LOOP_DELAY = 5 # s
USE_SIM = True
PWM_LED = False
NUM_LEDS = 14

SHUTDOWN_ON_STOP = False
STOP_PIN = 16

if USE_SIM:
    from light_strip_sim import LightStripSim
    controller = LightStripSim(NUM_LEDS)
elif PWM_LED:
    from light_controller import PwmLedController
    controller = PwmLedController()
else:
    from light_controller import LightController
    controller = LightController()

colours = Colours(NUM_LEDS, 0, 255)


def make_fake_beat(time_gap, duration, total_time):
    beats = []
    num_beats = math.floor(total_time/time_gap)

    for i in range(num_beats):
        beats.append({"start": i * time_gap,
                      "duration": duration})

    return beats


colour_scheme = "Neon1"

while True:
    beats = make_fake_beat(5, 2.5, 60)
    led_outs = colours.colour_pulse_on_beat(colour_scheme, beats)

    controller.play_led_output(led_outs)