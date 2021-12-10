import json
from Enumerations import LightingModes, colour_schemes

from colour_modes import Colours
from mood_based_colours import MoodBasedColours
from source.mode_handlers.music_reactive_mode_handler import MusicReactiveHandler
from source.mode_handlers.sequence_mode_handler import SequenceHandler
from source.mode_handlers.static_mode_handler import StaticHandler

USE_SIM = True
PWM_LED = False
NUM_LEDS = 5
LEDS_PER_COLOUR = 5

SPOTIFY_API_DELAY = 5 # s

START_SERVER = True  # Start a server for control over wifi
READ_CHUNK_SIZE = 1

# Select a lighting controller
if USE_SIM:
    from light_strip_sim import LightStripSim
    controller = LightStripSim(NUM_LEDS, LEDS_PER_COLOUR)
elif PWM_LED:
    from light_controller import PwmLedController
    controller = PwmLedController()
    controller.startup_pattern()
else:
    from light_controller import LightController
    controller = LightController(NUM_LEDS, LEDS_PER_COLOUR)
    controller.startup_pattern()

features_thresholds = {"danceability": 0.6,
                        "energy": 0.5,
                        "valence": 0.6}

# Create colours and mood objects
colours = Colours(int(NUM_LEDS/LEDS_PER_COLOUR), 0, 255)
mood_colours = MoodBasedColours(features_thresholds)

from source.communication.TCPServer import TCPServer
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

shutdown = False

# Create handlers for each mode
music_reactive_handler = MusicReactiveHandler(colours, mood_colours, controller)
static_handler = StaticHandler(colours, controller, static_colour)
sequence_handler = SequenceHandler(colours, controller, colour_schemes["Rave"], period=0.5)

handlers = {LightingModes.Static: static_handler,
            LightingModes.Sequence: sequence_handler,
            LightingModes.MusicReactive: music_reactive_handler}

def read_server_bit():
    global server_data

    data = server.receive(1)
    while data is not None and len(data) != 0:
        # print("recieved byte {}".format(data[0]))
        server_data.append(int(data[0]))
        if data[0] == 0x00:
            print("end of message reached")
            print(server_data[:-1].decode())
            json_dict = json.loads(server_data[:-1].decode())
            json_queue.append(json_dict)
            server_data = bytearray([])
        
        data = server.receive(1)  # read 1 byte at a time


def handle_message(json_dict):
    global static_colour
    global lighting_mode
    global shutdown
    global stop_lights

    method = json_dict["method"]

    if method == "setLedsActive":
        print("setLedsActive")
        if json_dict["value"] == 0:
            stop_lights = True
            # Stop any sequence playing and turn off the lights
            handlers[lighting_mode].stop_playing()
            controller.turn_off_leds()
        else:
            # resume playing by allowing the code for a specific loop to run
            stop_lights = False

    elif method == "setMode":
        print("setMode")
        new_mode = LightingModes(json_dict["value"])
        if new_mode != lighting_mode:
            handlers[lighting_mode].stop_playing()
            lighting_mode = new_mode

    elif method == "setBrightness":
        print("setBrightness")
        controller.set_master_brightness(json_dict["value"])

    elif method == "setStaticColour":
        print("setStaticColour")
        colour_json = json_dict["value"]
        if (0 <= colour_json["r"] <= 255) \
                    and (0 <= colour_json["g"] <= 255) \
                    and (0 <= colour_json["b"] <= 255):
            static_colour = (colour_json["r"], colour_json["g"], colour_json["b"])
        else:
            print("ERROR: Invalid colour provided")
        static_handler.set_uniform_colour(static_colour)

    elif method == "setColourSequence":
        print("setColourSequence")
        sequence_name = json_dict["value"]
        sequence_handler.colour_scheme = sequence_name
        sequence_handler.generate_sequence()

    elif method == "triggerSpotifyUpdate":
        print("triggerSpotifyUpdate")
        # Stop playing the current song but dont turn off the output so that
        # we re-check for a new song at the next update
        music_reactive_handler.stop_playing()

    elif method == "shutdown":
        print("shutdown")
        shutdown = True


while not shutdown:

    read_server_bit()
    if len(json_queue) > 0:
        handle_message(json_queue[-1])
        json_queue.pop(-1)

    if stop_lights:
        continue

    # Otherwise update the handler
    handlers[lighting_mode].update_handler()

    if USE_SIM:
        controller.update_simulation()


controller.turn_off_leds()
server.shutdown()
print("Shutdown complete")

