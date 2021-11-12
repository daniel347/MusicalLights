import time
import os
import numpy as np
import json
from Enumerations import LightingModes

from colour_modes import Colours
from mood_based_colours import MoodBasedColours, Key
from music_reactive_mode_handler import MusicReactiveHandler


USE_SIM = False
PWM_LED = False
NUM_LEDS = 144
LEDS_PER_COLOUR = 144

EXPORT_CREDENTIALS = True
SPOTIFY_API_DELAY = 5 # s


START_SERVER = True  # Start a server for control over wifi
READ_CHUNK_SIZE = 1

# Select a lighting controller
if USE_SIM:
    from light_strip_sim import LightStripSim
    controller = LightStripSim(NUM_LEDS)
elif PWM_LED:
    from light_controller import PwmLedController
    controller = PwmLedController()
    controller.startup_pattern()
else:
    from light_controller import LightController
    controller = LightController(NUM_LEDS, LEDS_PER_COLOUR)
    controller.startup_pattern()

# Create colours and mood objects
colours = Colours(int(NUM_LEDS/LEDS_PER_COLOUR), 0, 255)
mood_colours = MoodBasedColours(features_thresholds)

# Create handlers for each mode
music_reactive_handler = MusicReactiveHandler(colours, mood_colours, controller,
                                              EXPORT_CREDENTIALS)

if START_SERVER:
    from TCPServer import TCPServer
    server = TCPServer(1237)
    print("Listening for client")
    server.listen_for_client()

# Loop variables

stop_lights = False

lighting_mode = LightingModes.Static
static_colour = (255, 255, 255)
master_brightness = 1

server_data = bytearray([])

while True:

    if lighting_mode == LightingModes.MusicReactive and not stop_lights:
        music_reactive_handler.update_handler()

    elif lighting_mode == LightingModes.Static and not stop_lights:
        # A simple static light set
        controller.set_constant_colour([static_colour]*(NUM_LEDS/LEDS_PER_COLOUR))
            
    if (START_SERVER):
        data = server.receive(1)  # read 1 byte at a time
        if (data is not None):
            print("recieved bit")
            server_data.append(int(data[0]))
            if data[0] == 0x00:
                print("end of message reached")
                json_dict = json.loads(server_data[:-1].decode())
                method = json_dict["method"]

                if method == "setLedsActive":
                    print("setLedsActive")
                    if json_dict["value"] == 0:

                        stop_lights = True
                        # Stop any sequence playing and turn off the lights
                        controller.end_playing_sequence()
                        controller.turn_off_leds()
                        playing_sequence = False
                        current_track = None
                    else:
                        # resume playing by allowing the code for a specific loop to run
                        stop_lights = False

                elif method == "setMode":
                    print("setMode")
                    new_mode = LightingModes(json_dict["value"])
                    if new_mode != lighting_mode:
                        controller.end_playing_sequence()
                        controller.turn_off_leds()
                        playing_sequence = False
                        lighting_mode = new_mode

                elif method == "setStaticColour":
                    print("setStaticColour")
                    colour_json = json_dict["value"]
                    if (0 <= colour_json["r"] >= 255)\
                        (0 <= colour_json["g"] >= 255)\
                        (0 <= colour_json["b"] >= 255):
                        static_colour = (colour_json["r"], colour_json["g"], colour_json["b"])
                    else:
                        print("ERROR: Invalid colour provided")

print("Shutdown")

