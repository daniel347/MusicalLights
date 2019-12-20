import enum
import math
import struct
import time

import neopixel
import board

import BluetoothServer as bt

# ========LIGHT PARAMETERS========
DECAY_RATE = 350
INCREASE_RATE = 1500

N_lights = 5

brightnesses = [0] * N_lights
# ================================

# ====NEOPIXEL====

# ========LIGHTSTRIP PARAMETERS========
N_LEDS = 150
LED_ranges = [int(math.floor(N_LEDS / N_lights)) * n for n in range(1, N_lights + 1)]
# LED_ranges = [50, 90, 120, 140, 150]  # ie light one is LEDS 1- 50 and so on - needs to be updated for different n

FADE = 5  # fade 5 leds from each side of the boundary between two light groups for a smooth transition
LED_Colours = []

# spectrum mode params
OMEGA = 1  # controls the rate of changing colour with time
TWO_PI_N_LEDS = 2 * math.pi / N_LEDS  # constant value

TWO_PI_3 = 2 * math.pi / 3
FOUR_PI_3 = 2 * TWO_PI_3

# colours are functions of time and led strip position
red = lambda t, x : math.sin(OMEGA * t + TWO_PI_N_LEDS * x)
green = lambda t, x : math.sin(OMEGA * t + TWO_PI_N_LEDS * x + TWO_PI_3)
blue = lambda t, x : math.sin(OMEGA * t + TWO_PI_N_LEDS * x + FOUR_PI_3)

# =====================================

# ========BLUETOOTH PARAMETERS========
uuid = "1a7f34ab"  # arbitrary code to identify the right service
SERVICE_NAME = "MuscialLights Controller"

data_start_code = 100  # data codes
init_start_code = 101
end_code = 255  # indicates end of transmission

# NB : the start code is read seperately so is removed from these formats
# (byte) num_lights : (int) increase_rate : (int) decay_rate : (byte) colour_mode : (byte) end_code
init_format = "B I I B B"
init_size = 11  # 3 bytes and 2 4 byte ints

# (byte) start_code : (byte) light_1_value --- (byte) light_n_value : (byte) end_code
data_format = "B " * N_lights + "B"
data_size = 1 + N_lights

server = bt.BluetoothServerSDP(uuid, SERVICE_NAME)
# ====================================




def decay_grow(dt, light_output, brightness):
    """"Smooths out the changes in brightness using the defined decay and grow
    properties to smoothly vary the brightness"""

    max_dec = int(round(dt * DECAY_RATE))
    max_inc = int(round(dt * INCREASE_RATE))

    if (light_output - brightness) > 0:
        light_output -= (
            max_dec if (light_output - brightness) > max_dec else (light_output - brightness))
    elif (light_output - brightness) < 0:
        light_output += (
            max_inc if (brightness - light_output) > max_inc else (brightness - light_output))

    return light_output

def set_lights(colour, t):
    """"Sets the colour of the lights based on the mode and the time from the start"""
    x = 0
    if colour == ColourMode.spectrum:
        for i, range in enumerate(LED_ranges):
            while x < range:
                LED_val = (int(round(red(t, x) * brightnesses[i])),
                           int(round(green(t, x) * brightnesses[i])),
                           int(round(blue(t, x) * brightnesses[i]))) # rgb tuple for LED x

                x += 1
                # set to neopixel array

    if colour == ColourMode.blue:
        for i, range in enumerate(LED_ranges):
            while x < range:
                LED_val = (0, 0, brightnesses[i])  # rgb tuple for LED x

                x += 1
                # set to neopixel array

    if colour == ColourMode.green:
        for i, range in enumerate(LED_ranges):
            while x < range:
                LED_val = (0, brightnesses[i], 0)  # rgb tuple for LED x

                x += 1
                # set to neopixel array

    if colour == ColourMode.red:
        for i, range in enumerate(LED_ranges):
            while x < range:
                LED_val = (brightnesses[i], 0, 0)  # rgb tuple for LED x

                x += 1
                # set to neopixel array

    if colour == ColourMode.white:
        for i, range in enumerate(LED_ranges):
            while x < range:
                LED_val = (brightnesses[i], brightnesses[i], brightnesses[i])  # rgb tuple for LED x

                x += 1
                # set to neopixel array

    # show neopixel values


if __name__ == "__main__":

    # ========BLUETOOTH SETUP========

    start = time.time()
    last = time.time()
    now = time.time()
    # ========MAIN LOOP========
    while True:
        last = now
        now = time.time()

        code = ord(server.recieve_data(1))
        if code == data_start_code:
            data = server.recieve_data(data_size)
            tuple_data = struct.unpack(init_format, data)

            if tuple_data[-1] != end_code:
                # dont know how to handle this
                print("Check digit not correct!")

            brightnesses = [tuple_data[i] for i in range(N_lights)]


        if code == init_start_code:
            data = server.recieve_data(init_size)
            N_lights, INCREASE_RATE, DECAY_RATE, colour_mode, end = struct.unpack(init_format, data)
            if end != end_code:
                # dont know how to handle this
                print("Check digit not correct!")

class ColourMode(enum.Enum):
    spectrum = 1
    red = 2
    green = 3
    blue = 4
    white = 5



