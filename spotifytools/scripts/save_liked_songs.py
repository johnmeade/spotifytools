import pickle
from pathlib import Path

import spotipy

from ..spotify import export


HERE = Path(__file__).parent
SAVED_TRACK_PKL = HERE.joinpath('.artifacts', 'saved_tracks.pkl')


def save():
    auth_manager = spotipy.oauth2.SpotifyOAuth(scope='user-library-read', cache_path='/tmp/spotipy')
    api = spotipy.Spotify(auth_manager=auth_manager)
    export.saved_tracks(api, SAVED_TRACK_PKL, verbose=True)


def load():
    with SAVED_TRACK_PKL.open('rb') as f:
        return pickle.load(f)

# saved = load()
# for track in saved:
#     pass
