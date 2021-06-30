import spotipy
from spotipy.oauth2 import SpotifyOAuth

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id="b570fa330f38480caab0f1b1377f6057",
                                               client_secret="3349e3aef1764d92b175d5002e46852b",
                                               redirect_uri="https://github.com/robertjoy95/festivly.git",
                                               scope="user-library-read"))
results = sp.current_user_saved_tracks()
for idx, item in enumerate(results['items']):
    track = item['track']
    print(idx, track['artists'][0]['name'], " – ", track['name'])