from ..actions.query import get_liked_tracks

import spotipy

from pathlib import Path
import pickle


HERE = Path(__file__).parent


def main():
    # spotipy init
    auth_manager = spotipy.oauth2.SpotifyOAuth(scope='user-library-read', cache_path='/tmp/spotipy')
    api = spotipy.Spotify(auth_manager=auth_manager)
    # query
    print('Fetching all liked songs')
    liked = get_liked_tracks(api, pbar=True)
    # save
    print('Saving to disk')
    with open(HERE.joinpath('.artifacts', 'saved_tracks.pkl'), 'wb') as f:
        pickle.dump(liked, f)
    print('Done!')

    import json
    (HERE / '.artifacts' / 'saved_tracks.json').write_text(json.dumps(liked))


if __name__ == '__main__':
    main()
