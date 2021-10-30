import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy import SpotifyClientCredentials
import time
import os
import numpy as np

from colour_modes import Colours
from mood_based_colours import MoodBasedColours, Key

features_thresholds = {"danceability": 0.6,
                       "energy": 0.5,
                       "valence": 0.6}

USE_SIM = False
PWM_LED = False
NUM_LEDS = 144
LEDS_PER_COLOUR = 144

MAX_BRIGHTNESS = 1  # reduce this for a more subtle display

EXPORT_CREDENTIALS = True

START_SERVER = True  # Start a server for control over wifi
SERVER_MESSAGE_SIZE = 1
server_messages = {0xff : "quit",
                   0x00 : "stop_playing",
                   0x01 : "start_playing"}

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

# Connect to the spotify API
if EXPORT_CREDENTIALS:
    from export_credentials import export_credentials
    export_credentials()  # Exports spotify id, secret and redirect url to environment variables

scope = "playlist-read-private user-read-currently-playing"
client_credentials = SpotifyClientCredentials()
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

if START_SERVER:
    from TCPServer import TCPServer
    server = TCPServer(1237)
    print("Listening for client")
    server.listen_for_client()

# Loop variables
SPOTIFY_API_DELAY = 5 # s
last_api_call = 0

current_track = None
playing_sequence = False

stop_lights = False

while True:

    time_from_last_api_call = time.time() - last_api_call
    if time_from_last_api_call > SPOTIFY_API_DELAY and not playing_sequence and not stop_lights:
        last_api_call = time.time()
        # Check if there is music to play if we arent playing anything
        current_track = sp.current_user_playing_track()

        if current_track is not None and current_track["item"] is not None \
                and current_track["item"]["duration_ms"] - current_track["progress_ms"] > 10000:
            print("Currently playing {} - {}".format(current_track["item"]["name"],
                                                     current_track["item"]["artists"][0]["name"]))
            try:
                analysis = sp.audio_analysis(current_track["item"]["id"])
                features = sp.audio_features([current_track["item"]["id"]])[0]
            except Exception as e:
                print("Audio Analysis not accessable from Spotify API")
                print(e)
            else:
                audio_features = mood_colours.classify_music(features)
                led_outs = mood_colours.choose_track_lighting(colours,
                                                              audio_features,
                                                              analysis)
                led_outs.led_array = np.round(
                    led_outs.led_array * MAX_BRIGHTNESS).astype(np.uint8)

                # call the api again for the accurate timing
                current_track = sp.current_user_playing_track()
                time_in = current_track["progress_ms"] / 1000
                controller.start_playing_sequence(led_outs, time_in)
                playing_sequence = True
        else:
            print("Nothing playing at the moment")

    if (playing_sequence):
        ret = controller.update_playing_sequence()
        if ret == 2:
            # Final change reached, end the sequence
            controller.end_playing_sequence()
            playing_sequence = False
            
    if (START_SERVER):
        data = server.receive(SERVER_MESSAGE_SIZE)
        if (data is not None and len(data) == SERVER_MESSAGE_SIZE):
            if data[0] == 0x00:
                # stop playing
                stop_lights = True
                controller.end_playing_sequence()
                controller.turn_off_leds()
                playing_sequence = False
                current_track = None

            if data[0] == 0x01:
                # resume playing
                stop_lights = False

            if data[0] == 0xff:
                # shutdown
                controller.shutdown()
                break

print("Shutdown")

