import json
import pickle
from pathlib import Path

from ..actions.query import get_liked_tracks
from ._auth import get_api


HERE = Path(__file__).parent


def main():
    api = get_api(scope='user-library-read')
    # query
    print('Fetching all liked songs')
    liked = get_liked_tracks(api, pbar=True)
    # save
    print('Saving to disk')
    with open(HERE.joinpath('.artifacts', 'saved_tracks.pkl'), 'wb') as f:
        pickle.dump(liked, f)

    (HERE / '.artifacts' / 'saved_tracks.json').write_text(json.dumps(liked))

    print('Done!')


if __name__ == '__main__':
    main()
