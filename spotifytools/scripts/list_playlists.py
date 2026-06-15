from ._auth import get_api

from pathlib import Path


HERE = Path(__file__).parent


def main():
    api = get_api(scope='user-library-read')
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
