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

LOOP_DELAY = 5 # s
USE_SIM = False
PWM_LED = True
NUM_LEDS = 1

USE_GPIO = True
SHUTDOWN_ON_STOP = True
STOP_PIN = 21

MAX_BRIGHTNESS = 1  # reduce this for a more subtle display

EXPORT_CREDENTIALS = True

if EXPORT_CREDENTIALS:
    from export_credentials import export_credentials
    export_credentials()  # Exports spotify id, secret and redirect url to environment variables

gpio_break = None
if USE_GPIO:
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(STOP_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    gpio_break = lambda : GPIO.input(STOP_PIN) == 1

if USE_SIM:
    from light_strip_sim import LightStripSim
    controller = LightStripSim(NUM_LEDS)
elif PWM_LED:
    from light_controller import PwmLedController
    controller = PwmLedController()
    controller.startup_pattern()
else:
    from light_controller import LightController
    controller = LightController()
    controller.startup_pattern()

colours = Colours(NUM_LEDS, 0, 255)
mood_colours = MoodBasedColours(features_thresholds)

scope = "playlist-read-private user-read-currently-playing"
client_credentials = SpotifyClientCredentials()
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

while True:

    last_run = time.time()
    current_track = sp.current_user_playing_track()
    ret = 0

    # only play if there is more than 10s of the track
    if current_track is not None and \
            current_track["item"] is not None and \
            current_track["item"]["duration_ms"] - current_track["progress_ms"] > 10000:
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
            led_outs = mood_colours.choose_track_lighting(colours, audio_features, analysis)
            led_outs.led_array = np.round(led_outs.led_array * MAX_BRIGHTNESS).astype(np.uint8)

            # call the api again for the accurate timing
            current_track = sp.current_user_playing_track()
            time_in = current_track["progress_ms"] / 1000
            ret = controller.play_led_output(led_outs, time_in, gpio_break)
    else:
        print("Nothing playing at the moment")
        
    if ret == -1:
        break

    # limit the speed of the loop, to not reach the limit with the spotify API
    time_from_last_run = time.time() - last_run
    if time_from_last_run < LOOP_DELAY:
        time.sleep(LOOP_DELAY - time_from_last_run)
        
controller.shutdown()
if SHUTDOWN_ON_STOP:
    os.system("sudo shutdown -h now")
