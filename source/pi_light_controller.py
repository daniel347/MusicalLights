import math
import struct
import time
from colour_mode import ColourMode

import neopixel
import board

import BluetoothServer as bt

# ========LIGHT PARAMETERS========
DECAY_RATE = 350
INCREASE_RATE = 1500

N_lights = 5

brightnesses = [0] * N_lights
# ================================

# ========LIGHTSTRIP PARAMETERS========
N_LEDS = 150
LED_ranges = [int(math.floor(N_LEDS / N_lights)) * n for n in range(1, N_lights + 1)]
# LED_ranges = [50, 90, 120, 140, 150]  # ie light one is LEDS 1- 50 and so on - needs to be updated for different n

FADE = 5  # fade 5 leds from each side of the boundary between two light groups for a smooth transition
LED_values = [(0,0,0)] * N_LEDS
# =====================================

# ========NEOPIXEL SETUP========
pixels = neopixel.NeoPixel(board.D18, N_LEDS, auto_write=False)
pixels.fill((0,150,0))

# ==============================

# ========COLOUR MODE OPTIONS========
# spectrum mode params
OMEGA = 1  # controls the rate of changing colour with time
TWO_PI_N_LEDS = 2 * math.pi / N_LEDS  # constant value

TWO_PI_3 = 2 * math.pi / 3
FOUR_PI_3 = 2 * TWO_PI_3

# colours are functions of time and led strip position
# sinusiodal functions between 0 and 1 of varying phase produce the shifting colour spectrum effect
red = lambda t, x: (1.0 + math.sin(OMEGA * t + TWO_PI_N_LEDS * x)) / 2.0
green = lambda t, x: (1.0 + math.sin(OMEGA * t + TWO_PI_N_LEDS * x + TWO_PI_3)) / 2.0
blue = lambda t, x: (1.0 + math.sin(OMEGA * t + TWO_PI_N_LEDS * x + FOUR_PI_3)) / 2.0

# colour array for other colour modes - set over bluetooth
colours = [(255, 0, 0),
           (0, 255, 0),
           (0, 0, 255)]

# alternating two
alternating_T = 1  # time to change from one colour to the next

# beat change mode
colour_index = 0  # the index of the colour being used right now
beat = False

colour_mode = ColourMode.spectrum
# =====================================

# ========BLUETOOTH PARAMETERS========
uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee" # arbitrary code to identify the right service
SERVICE_NAME = "MuscialLights Controller"

data_start_code = 100  # data codes
init_start_code = 101
colour_set_start_code = 102
shutdown_code = 103
end_code = 255  # indicates end of transmission

# NB : the start code is read seperately so is removed from these formats
# (byte) num_lights : (int) increase_rate : (int) decay_rate : (byte) colour_mode : (byte) end_code
init_format = "B I I B B"
init_size = 11  # 3 bytes and 2 4 byte ints

# (byte) start_code : (byte) light_1_value --- (byte) light_n_value : (byte) beat : (byte) end_code
data_format = "B " * N_lights + "B B"
data_size = 1 + N_lights

# (byte) num_colours
colour_start_format = "B"
colour_start_size = 1

# (byte) red_val : (byte) green_val : (byte) blue_val
colour_format = "B B B"
colour_size = 3

# (byte) end_code  - > no need for format as it will always be a single byte
print("Starting bluetooth server ...")
TIMEOUT = 1  # timeout for read operations in seconds
server = bt.BluetoothServerSDP(uuid, SERVICE_NAME, )
# ====================================


def decay_grow_colour(dt, colour_output, colour_setval):
    """"Smooths out the changes in brightness using the defined decay and grow
    properties to smoothly vary the brightness.
    colour_output is the current value of the lights and colour_setval is the desired value"""

    max_dec = int(round(dt * DECAY_RATE))
    max_inc = int(round(dt * INCREASE_RATE))

    new_colour = []

    for i, (col_comp, setval) in enumerate(zip(colour_output, colour_setval)):
        if (col_comp - setval) > 0:
            new_colour[i] = col_comp - (max_dec if (col_comp - setval) > max_dec else (col_comp - setval))
        elif (col_comp - setval) < 0:
            new_colour[i] = col_comp + (max_inc if (setval - col_comp) > max_inc else (setval - col_comp))

    return tuple(new_colour)

def fade_transition(range_val):
    """Interpolates linearly at the boundary between light groups for a smooth transition"""
    # NB values of the LEDS at the start and end points of the fade are unchanged
    start_point = range_val - 1 - FADE
    end_point = range_val - 1 + FADE

    # start and end colours
    start_col = LED_values[start_point]
    end_col = LED_values[end_point]

    # find the change in RGB values from one end of the fade to the other
    gradient = tuple(e-s for s, e in zip(start_col, end_col))

    # update array for the faded section only
    for i in range(start_point, end_point):
        LED_values[i] = tuple([int(round((comp * (i - start_point))/(end_point - start_point))) for comp in gradient])

def set_lights(t, dt, beat):
    """"Sets the colour of the lights based on the mode and the time from the start"""
    x = 0
    if colour_mode == ColourMode.spectrum:
        for i, range in enumerate(LED_ranges):
            while x < range:
                LED_val = (int(round(red(t, x) * brightnesses[i])),
                           int(round(green(t, x) * brightnesses[i])),
                           int(round(blue(t, x) * brightnesses[i])))  # rgb tuple for LED x

                LED_values[x] = decay_grow_colour(dt, LED_values[x], LED_val)
                x += 1

    if colour_mode == ColourMode.single_colour:
        # uses first colour in colours list
        c = colours[0]
        for i, range in enumerate(LED_ranges):
            while x < range:
                LED_val = (int(round((c[0] * brightnesses[i]) / 255)),
                           int(round((c[1] * brightnesses[i]) / 255)),
                           int(round((c[2] * brightnesses[i]) / 255)))

                LED_values[x] = decay_grow_colour(dt, LED_values[x], LED_val)
                x += 1

    if colour_mode == ColourMode.alternating_two:
        c = colours[math.floor(t / alternating_T) % 2]
        for i, range in enumerate(LED_ranges):
            while x < range:
                LED_val = (int(round((c[0] * brightnesses[i]) / 255)),
                           int(round((c[1] * brightnesses[i]) / 255)),
                           int(round((c[2] * brightnesses[i]) / 255)))

                LED_values[x] = decay_grow_colour(dt, LED_values[x], LED_val)
                x += 1


    if colour_mode == ColourMode.change_on_beat:
        if beat:
            colour_index = (colour_index + 1) % len(colours)

        c = colours[colour_index]
        for i, range in enumerate(LED_ranges):
            while x < range:
                LED_val = (int(round((c[0] * brightnesses[i]) / 255)),
                           int(round((c[1] * brightnesses[i]) / 255)),
                           int(round((c[2] * brightnesses[i]) / 255)))

                LED_values[x] = decay_grow_colour(dt, LED_values[x], LED_val)
                x += 1

def update_neopixels():
    """Calculates the fade properties for each lED sets the corresponding neopixel value"""
    # remove the last value since we do not need a fade at the end
    for pos in LED_ranges[:-1]:
        fade_transition(pos)

    for pos, val in enumerate(LED_values):
        pixels[pos] = val  # set the neopixel values

    pixels.show()

def startup_pattern():
    """"Light pattern to play at startup"""
    start_pattern = [(50, 0, 0),
                     (75, 100, 0),
                     (0, 255, 0),
                     (0, 100, 75),
                     (0, 0, 50)]  # like a small spectrum wave

    speed = 0.01 # time delay between moving the wave up one pixel

    for wave_pos in range(N_LEDS - len(start_pattern)):
        pixels.fill((0,0,0))
        for i, c in enumerate(start_pattern):
            pixels[wave_pos + i] = c

        pixels.show()
        time.sleep(speed)

if __name__ == "__main__":

    # run LED startup pattern
    startup_pattern()

    start = time.time()
    last = time.time()
    now = time.time()

    # ========MAIN LOOP========
    while True:
        last = now
        now = time.time()
        
        first_byte = server.recieve_data(1)
        if (first_byte != -1):  
            # if there is data to read
            code = ord(first_byte)
            if code == data_start_code:
                data = server.recieve_data(data_size)
                print(data)
                tuple_data = struct.unpack(data_format, data)

                if tuple_data[-1] != end_code:
                    # dont know how to handle this
                    print("Check digit not correct!")

                beat = bool(tuple_data[-2])
                brightnesses = [tuple_data[i] for i in range(N_lights)]

            elif code == init_start_code:
                data = server.recieve_data(init_size)
                N_lights, INCREASE_RATE, DECAY_RATE, colour_mode, end = struct.unpack(init_format, data)
                if end != end_code:
                    # dont know how to handle this
                    print("Check digit not correct!")

            elif code == colour_set_start_code:
                num_colours, = struct.unpack(colour_start_format, server.recieve_data(colour_start_size))

                for i in range(num_colours):
                    colour_data = server.recieve_data(colour_size)
                    colours[i] = struct.unpack(colour_format, colour_data)

                if ord(server.recieve_data(1)) != end_code:
                    # dont know how to handle this
                    print("Check digit not correct")

            elif code == shutdown_code:
                server.close_socket()
                pixels.fill((0,0,0))
                    
        set_lights(now - start, now - last, beat)
        update_neopixels()
