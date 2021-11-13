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

features_thresholds = {}

# Create colours and mood objects
colours = Colours(int(NUM_LEDS/LEDS_PER_COLOUR), 0, 255)
mood_colours = MoodBasedColours(features_thresholds)

# Create handlers for each mode
music_reactive_handler = MusicReactiveHandler(colours, mood_colours, controller,
                                              EXPORT_CREDENTIALS)

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
json_queue = []

mode_handler = music_reactive_handler  # The handler for the particular mode you are the world

shutdown = False

def read_server_bit():
    global server_data

    data = server.receive(1)  # read 1 byte at a time
    while (data is not None):
        print("recieved bit")
        server_data.append(int(data[0]))
        if data[0] == 0x00:
            print("end of message reached")
            json_dict = json.loads(server_data[:-1].decode())
            json_queue.append(json_dict)
            server_data = bytearray([])


def handle_message(json_dict):
    global static_colour
    global lighting_mode

    method = json_dict["method"]

    if method == "setLedsActive":
        print("setLedsActive")
        if json_dict["value"] == 0:
            stop_lights = True
            # Stop any sequence playing and turn off the lights
            mode_handler.stop_playing()
        else:
            # resume playing by allowing the code for a specific loop to run
            stop_lights = False

    elif method == "setMode":
        print("setMode")
        new_mode = LightingModes(json_dict["value"])
        if new_mode != lighting_mode:
            mode_handler.stop_playing()
            lighting_mode = new_mode

    elif method == "setStaticColour":
        print("setStaticColour")
        colour_json = json_dict["value"]
        if (0 <= colour_json["r"] >= 255) \
                    (0 <= colour_json["g"] >= 255) \
                    (0 <= colour_json["b"] >= 255):
            static_colour = (colour_json["r"], colour_json["g"], colour_json["b"])
        else:
            print("ERROR: Invalid colour provided")


while not shutdown:

    read_server_bit()
    if len(json_queue) > 0:
        handle_message(json_queue[-1])

    if stop_lights:
        continue

    # Otherwise update the handlers
    if lighting_mode == LightingModes.MusicReactive:
        music_reactive_handler.update_handler()

    elif lighting_mode == LightingModes.Static:
        # A simple static light set
        controller.set_constant_colour([static_colour]*(NUM_LEDS/LEDS_PER_COLOUR))

    elif lighting_mode == LightingModes.Pattern:
        pass



print("Shutdown")

