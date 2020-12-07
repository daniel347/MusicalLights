import spotipy
import sys
import spotipy.util as util
from spotipy.oauth2 import SpotifyOAuth

import spotipy
from spotipy.oauth2 import SpotifyOAuth

from colour_modes import Colours

scope = "playlist-read-private"
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

playlist_name = "Christmas Songs"
playlist_tracks = ""
playlists = sp.current_user_playlists()

for playlist in playlists["items"]:
    if playlist["name"] == playlist_name:
        playlist_tracks = sp.playlist_tracks(playlist["id"])

for track in playlist_tracks["items"]:
    print("{} - {}".format(track["track"]["name"], track["track"]["artists"][0]["name"]))
    analysis = sp.audio_analysis(track["track"]["id"])
    colours = Colours(20)
    led_outs = colours.colour_change_on_beat([(1,0,0), (0,1,0), (0,0,1)], analysis["beats"])
    print(led_outs)

print("test")

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