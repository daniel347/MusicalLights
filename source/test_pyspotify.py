import spotipy
import sys
import spotipy.util as util
from spotipy.oauth2 import SpotifyOAuth

import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy import SpotifyClientCredentials
import numpy as np

from colour_modes import Colours
from light_strip_sim import LightStripSim

sim = LightStripSim(150)
colours = Colours(150, 0, 255)

scope = "playlist-read-private user-read-currently-playing"
client_credentials = SpotifyClientCredentials()
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

playlist_name = "Christmas Songs"
playlist_tracks = ""
playlists = sp.current_user_playlists()

led_outs_dict = {}

"""
for playlist in playlists["items"]:
    if playlist["name"] == playlist_name:
        playlist_tracks = sp.playlist_tracks(playlist["id"])

for track in playlist_tracks["items"]:
    track_name = track["track"]["name"]
    print("{} - {}".format(track["track"]["name"], track["track"]["artists"][0]["name"]))
    analysis = sp.audio_analysis(track["track"]["id"])
    colours = Colours(150)
    led_outs = colours.colour_fade_on_beat(np.array([[255,0,0], [0,255,0], [0,0,255]]), analysis["beats"], interpolated_points=20)
    led_outs_dict[track_name] = led_outs
    
"""
value = sp.current_user_playing_track()
print("Currently playing")
analysis = sp.audio_analysis(value["item"]["id"])
led_outs = colours.colour_fade_on_beat(np.array([[255,0,0], [255,0,0], [255,0,0]]), analysis["beats"], duration_shift=0.8)
led_outs = colours.modulate_brightness_on_loudness(led_outs, analysis["segments"], interpolated_points=5, blur_samples=1)

# call the api again for the accurate timing
value = sp.current_user_playing_track()
time_in = value["progress_ms"]/1000
sim.play_led_output(led_outs, time_in)

"""

scope = 'user-library-read'

if len(sys.argv) > 1:
    username = sys.argv[1]
else:
    print("Usage: %s username" % (sys.argv[0],))
    sys.exit()

token = util.prompt_for_user_token(username, scope)

if token:
    sp = spotipy.Spotify(auth=token)
    results = sp.current_user_saved_tracks()
    for item in results['items']:
        track = item['track']
        print(track['name'] + ' - ' + track['artists'][0]['name'])
else:
    print("Can't get token for", username)
    
"""

"""

auth_manager = SpotifyOAuth(scope='playlist-modify-public')
token = auth_manager.get_access_token()

spotify = spotipy.Spotify(auth_manager=auth_manager)

playlists = spotify.current_user_playlists()
print(playlists)


"""