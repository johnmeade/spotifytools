from pathlib import Path

import pickle
import spotipy

from ..actions.query import get_curr_birp_tracks


def main():
    # spotipy init
    auth_manager = spotipy.oauth2.SpotifyOAuth(scope='user-library-read', cache_path='/tmp/spotipy')
    api = spotipy.Spotify(auth_manager=auth_manager)
    # query
    print('Fetching playlists')
    ts = get_curr_birp_tracks(api)
    print('---')
    print(ts)
    print('---')


if __name__ == '__main__':
    main()
