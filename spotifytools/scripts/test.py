import spotipy
from ..actions.queue import john_shuffle


def main():
    auth_manager = spotipy.oauth2.SpotifyOAuth(scope='user-library-read', cache_path='/tmp/spotipy')
    api = spotipy.Spotify(auth_manager=auth_manager)
    john_shuffle(api)


if __name__ == '__main__':
    main()
