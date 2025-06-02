import spotipy

from pathlib import Path
import pickle


HERE = Path(__file__).parent


def main():
    # spotipy init
    auth_manager = spotipy.oauth2.SpotifyOAuth(scope='user-library-read', cache_path='/tmp/spotipy')
    api = spotipy.Spotify(auth_manager=auth_manager)
    # query
    print('Fetching playlists')
    pls = api.current_user_playlists()
    print('---')
    print(pls)
    print('---')
    for p in pls["items"]:
        print(p['name'])


if __name__ == '__main__':
    main()
