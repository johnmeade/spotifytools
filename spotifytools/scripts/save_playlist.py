import json
import pickle
from pathlib import Path

from ._auth import get_api
from ..actions.query import _paginated_items


HERE = Path(__file__).parent


def pick_playlist(api):
    result = api.current_user_playlists()
    playlists = result['items']
    while result['next']:
        result = api.next(result)
        playlists.extend(result['items'])

    print('\nYour playlists:')
    for i, pl in enumerate(playlists):
        print(f'  {i + 1:>2}. {pl["name"]}  ({pl["tracks"]["total"]} tracks)')

    while True:
        raw = input('\nChoose a playlist (number): ').strip()
        if raw.isdigit() and 1 <= int(raw) <= len(playlists):
            return playlists[int(raw) - 1]
        print(f'  Enter a number between 1 and {len(playlists)}.')


def main():
    api = get_api(scope='user-library-read')
    pl = pick_playlist(api)

    print(f'\nFetching tracks from "{pl["name"]}"...')
    items = _paginated_items(
        lambda limit, offset: api.playlist_items(pl['id'], limit=limit, offset=offset),
        pbar=True,
    )
    tracks = [item['track'] for item in items if item.get('track')]

    slug = pl['name'].lower().replace(' ', '_')
    out_dir = HERE / '.artifacts'
    out_dir.mkdir(exist_ok=True)

    pkl_path = out_dir / f'playlist_{slug}.pkl'
    json_path = out_dir / f'playlist_{slug}.json'

    with open(pkl_path, 'wb') as f:
        pickle.dump(tracks, f)
    json_path.write_text(json.dumps(tracks))

    print(f'Saved {len(tracks)} tracks to {json_path}')


if __name__ == '__main__':
    main()
