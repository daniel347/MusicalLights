import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy import SpotifyClientCredentials

from colour_modes import Colours
from light_strip_sim import LightStripSim
from mood_based_colours import MoodBasedColours, Key
from light_sequence import LightSequence

import random

features_thresholds = {"danceability": 0.6,
                       "energy": 0.5,
                       "valence": 0.6}

sim = LightStripSim(1)
colours = Colours(1, 0, 255)
mood_colours = MoodBasedColours(features_thresholds)

scope = "playlist-read-private user-read-currently-playing"
client_credentials = SpotifyClientCredentials()
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

playlist_name = "Christmas Songs"
playlist_tracks = ""
playlists = sp.current_user_playlists()

if __name__ == "__main__":
    value = sp.current_user_playing_track()
    if value is not None:
        print("Currently playing {}".format(value["item"]["name"]))
        analysis = sp.audio_analysis(value["item"]["id"])
        print(analysis["sections"][1]["start"])

        features = sp.audio_features([value["item"]["id"]])[0]
        audio_features = mood_colours.classify_music(features)

        possible_colour_schemes = colours.choose_colour_schemes_for_time_signature(
                                                        audio_features.time_signature)
        colour_scheme = random.choice(possible_colour_schemes)

        high_tempo = audio_features.tempo > 120
        low_tempo = audio_features.tempo < 80

        led_sections = []
        section_times = []

        for section in analysis["sections"]:
            section_times.append(section["start"])
            key = None
            if section["key"] != -1:
                key = Key(section["key"])

            major = bool(section["mode"]) if section["mode"] != -1 else None

            if colour_scheme.shape[0] <= 2:
                # for colour schemes that are very short add more variety
                colour_scheme = random.choice(possible_colour_schemes)

            mode = random.choice(colours.colour_functions)
            speed = random.choice(["bars", "beats", "tatums"])
            led_sections.append(getattr(colours, mode)(colour_scheme, analysis[speed]))

        section_times.append(section["start"] + section["duration"])
        led_outs = LightSequence(sequence_list_time=led_sections,
                                 switch_times=section_times)

        # call the api again for the accurate timing
        value = sp.current_user_playing_track()
        time_in = value["progress_ms"] / 1000
        sim.play_led_output(led_outs, time_in)
    else:
        print("Nothing playing at the moment")