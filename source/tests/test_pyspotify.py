import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy import SpotifyClientCredentials

from colour_modes import Colours
from light_strip_sim import LightStripSim

sim = LightStripSim(1)
colours = Colours(1, 0, 255)

scope = "playlist-read-private user-read-currently-playing"
client_credentials = SpotifyClientCredentials()
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

playlist_name = "Christmas Songs"
playlist_tracks = ""
playlists = sp.current_user_playlists()

"""
## To read a playlist and all its songs

for playlist in playlists["items"]:
    if playlist["name"] == playlist_name:
        playlist_tracks = sp.playlist_tracks(playlist["id"])

for track in playlist_tracks["items"]:
    track_name = track["track"]["name"]
    print("{} - {}".format(track["track"]["name"], track["track"]["artists"][0]["name"]))
    analysis = sp.audio_analysis(track["track"]["id"])
    features = sp.audio_features([track["item"]["id"]])[0]
    
"""
## To find the current song playing and analyse that

current_track = sp.current_user_playing_track()
if current_track is not None:
    print("Currently playing {}".format(current_track["item"]["name"]))
    analysis = sp.audio_analysis(current_track["item"]["id"])
    features = sp.audio_features([current_track["item"]["id"]])[0]


    # call the api again for the accurate timing to start an led sequence
    current_track = sp.current_user_playing_track()
    time_in = current_track["progress_ms"] / 1000
else:
    print("Nothing playing at the moment")