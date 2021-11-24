from export_credentials import export_credentials
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy import SpotifyClientCredentials
import numpy as np

import time


class MusicReactiveHandler():

    def __init__(self, colours, mood_colours, controller, export_creds=True, api_delay=5):
        self.controller = controller
        self.colours = colours
        self.mood_colours = mood_colours

        if export_creds:
            export_credentials()

        self.api_delay = api_delay

        self.sp = None  # the Spotify API library object
        self.current_track = None
        self.playing_sequence = False

        self.last_api_call = 0

    def connect_to_spotify(self):
        # Connect to the spotify API
        scope = "playlist-read-private user-read-currently-playing"
        client_credentials = SpotifyClientCredentials()
        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

    def get_track_playing(self):
        self.current_track = self.sp.current_user_playing_track()

        if self.current_track is not None and self.current_track["item"] is not None \
                and self.current_track["item"]["duration_ms"] - self.current_track["progress_ms"] > 10000:
            return True

        # The track is not suitable for lights, or nothing is playing
        self.current_track = None
        return False


    def start_playing_to_music(self):
        # Check if music is playing, and if so start playing lights in sync
        try:
            analysis = self.sp.audio_analysis(self.current_track["item"]["id"])
            features = self.sp.audio_features([self.current_track["item"]["id"]])[0]
        except Exception as e:
            print("Audio Analysis not accessable from Spotify API")
            print(e)
            return False
        else:
            audio_features = self.mood_colours.classify_music(features)
            led_outs = self.mood_colours.choose_track_lighting(self.colours,
                                                          audio_features,
                                                          analysis)

            # call the api again for the accurate timing
            current_track = self.sp.current_user_playing_track()
            time_in = current_track["progress_ms"] / 1000
            self.controller.start_playing_sequence(led_outs, time_in)
            return True

    def update_handler(self):

        if self.playing_sequence:
            # update the sequence
            ret = self.controller.update_playing_sequence()
            if ret == 2:
                # Final change reached, end the sequence
                self.controller.end_playing_sequence()
                self.playing_sequence = False
        else:
            time_from_last_api_call = time.time() - self.last_api_call
            if time_from_last_api_call > self.api_delay:
                self.last_api_call = time.time()

                # Reconect to spotify if we have deleted the prior connection
                if self.sp is None:
                    self.connect_to_spotify()
                # Check if there is music to play if we arent playing anything
                if self.get_track_playing():
                    if self.start_playing_to_music():
                        self.playing_sequence = True
                        print("Currently playing {} - {}".format(self.current_track["item"]["name"],
                                                                 self.current_track["item"]["artists"][0]["name"]))

    def stop_playing(self):
        # Final change reached, end the sequence
        self.controller.end_playing_sequence()
        self.playing_sequence = False
        self.current_track = None


