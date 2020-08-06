from time import sleep
from tqdm import tqdm


RATE_LIMIT_SLEEP = 0.1
MAX_LIMIT = 50


def _all_paginated_items(func, pbar=False):
    items = []
    offset = 0
    total = 0
    progress = None
    while True:
        # obtain and read chunk
        chunk = func(limit=MAX_LIMIT, offset=offset)
        total = chunk['total']
        chunk_items = chunk['items']
        # progress bar
        if pbar:
            progress = progress or tqdm(total=total)
            progress.update(len(chunk_items))
        # accumulate
        items += chunk_items
        offset += len(chunk_items)
        if offset >= total:
            break
        sleep(RATE_LIMIT_SLEEP)
    return items


def all_liked_albums(spotify, pbar=False):
    items = _all_paginated_items(spotify.current_user_saved_albums, pbar)
    return [ item['album'] for item in items ]


def all_liked_tracks(spotify, pbar=False):
    items = _all_paginated_items(spotify.current_user_saved_tracks, pbar)
    return [ item['track'] for item in items ]


def track(title, artist='', limit=10):
    'search for track and attempt exact match'

    results = api.search(q=f'{title} {artist}', limit=limit, type='track')
    results = results['tracks']['items']

    # naive check for exact match
    title = title.lower().strip()
    artist = artist.lower().strip()
    for result in results:
        if result['name'].lower().strip() == title:
            for res_artist in result['artists']:
                if res_artist['name'].lower().strip() == artist:
                    return result, results

    return None, results
