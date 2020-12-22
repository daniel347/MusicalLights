import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy import SpotifyClientCredentials
import time
import RPi.GPIO as GPIO
import os

from colour_modes import Colours
from light_strip_sim import LightStripSim
from light_controller import PwmLedController, LightController
from mood_based_colours import MoodBasedColours, Key
from export_credentials import export_credentials

export_credentials()  # Exports spotify id, secret and redirect url to environment variables

features_thresholds = {"danceability": 0.6,
                       "energy": 0.5,
                       "valence": 0.6}

LOOP_DELAY = 5 # s
USE_SIM = True
PWM_LED = False
NUM_LEDS = 1

SHUTDOWN_ON_STOP = False
STOP_PIN = 16
GPIO.setmode(GPIO.BCM)
GPIO.setup(STOP_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
print(GPIO.input(STOP_PIN)) 

if USE_SIM:
    controller = LightStripSim(NUM_LEDS)
elif PWM_LED:
    controller = PwmLedController()
else:
    controller = LightController()
colours = Colours(NUM_LEDS, 0, 255)
mood_colours = MoodBasedColours(features_thresholds)

scope = "playlist-read-private user-read-currently-playing"
client_credentials = SpotifyClientCredentials()
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

while GPIO.input(STOP_PIN) == 0:
    last_run = time.time()
    current_track = sp.current_user_playing_track()

    # only play if there is more than 10s of the track
    if current_track is not None and \
            current_track["item"]["duration_ms"] - current_track["progress_ms"] > 10000:
        print("Currently playing {} - {}".format(current_track["item"]["name"],
                                                 current_track["item"]["artists"][0]["name"]))
        analysis = sp.audio_analysis(current_track["item"]["id"])
        features = sp.audio_features([current_track["item"]["id"]])[0]

        audio_features = mood_colours.classify_music(features)
        led_outs = mood_colours.choose_track_lighting(colours, audio_features, analysis)

        # call the api again for the accurate timing
        current_track = sp.current_user_playing_track()
        time_in = current_track["progress_ms"] / 1000
        controller.play_led_output(led_outs, time_in)
    else:
        print("Nothing playing at the moment")

    # limit the speed of the loop, to not reach the limit with the spotify API
    time_from_last_run = time.time() - last_run
    if time_from_last_run < LOOP_DELAY:
        time.sleep(LOOP_DELAY - time_from_last_run)
        
controller.shutdown()
if SHUTDOWN_ON_STOP:
    os.system("sudo shutdown -h now")
