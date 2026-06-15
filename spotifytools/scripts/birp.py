from pathlib import Path

import pickle

from ..actions.query import get_curr_birp_tracks
from ._auth import get_api


def main():
    api = get_api(scope='user-library-read')
    # query
    print('Fetching playlists')
    ts = get_curr_birp_tracks(api)
    print('---')
    print(ts)
    print('---')


if __name__ == '__main__':
    main()
