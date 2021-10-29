import blynklib
from colour_modes import Colours
import numpy as np
import math

LOOP_DELAY = 5 # s
USE_SIM = True
PWM_LED = False
NUM_LEDS = 14

SHUTDOWN_ON_STOP = False
STOP_PIN = 16

if USE_SIM:
    from light_strip_sim import LightStripSim
    controller = LightStripSim(NUM_LEDS, 1)
elif PWM_LED:
    from light_controller import PwmLedController
    controller = PwmLedController()
else:
    from light_controller import LightController
    controller = LightController()

colours = Colours(NUM_LEDS, 0, 255)

# These are here for reference only I believe
BLYNK_TEMPLATE_ID = "TMPLUms5R1OZ"
BLYNK_DEVICE_NAME = "LEDController"
# ----

BLYNK_AUTH = "ZpP-wKt_AOepQOlz4no_X9ynTMT9wA4x"

# initialize Blynk
blynk = blynklib.Blynk(BLYNK_AUTH)

WRITE_EVENT_PRINT_MSG = "[WRITE_VIRTUAL_PIN_EVENT] Pin: V{} Value: '{}'"


# register handler for virtual pin V4 write event
@blynk.handle_event('write V0')
def write_virtual_pin_handler(pin, value):
    print(WRITE_EVENT_PRINT_MSG.format(pin, value))
    led_arr = np.array([[int(value), int(value), int(value)]]*NUM_LEDS)
    controller.__set_all_leds(led_arr)

###########################################################
# infinite loop that waits for event
###########################################################
while True:
    print("Running!")
    blynk.run()