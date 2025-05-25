from time import sleep
from tqdm import tqdm
from datetime import datetime


RATE_LIMIT_SLEEP = 0.1
MAX_LIMIT = 50


def _paginated_items(func, pbar=False, limit=None):
    items = []
    offset = 0
    total = 0
    limit = limit or float('inf')
    progress = None
    while True:
        api_limit = min(MAX_LIMIT, limit - len(items))
        if api_limit <= 0:
            break
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
        if offset >= total or len(items) >= limit:
            break
        sleep(RATE_LIMIT_SLEEP)
    return items


def get_liked_albums(spotify, pbar=False, limit=None):
    items = _paginated_items(spotify.current_user_saved_albums, pbar, limit)
    return [ item['album'] for item in items ]


def get_liked_tracks(spotify, pbar=False, limit=None):
    items = _paginated_items(spotify.current_user_saved_tracks, pbar, limit)
    return [ item['track'] for item in items ]


# def get_new_rec_releases(spotify, pbar=False, limit=None):
#     items = _paginated_items(spotify., pbar, limit)
#     return [ item['track'] for item in items ]


def get_curr_birp_tracks(spotify):
    mo = datetime.now().strftime("%B")
    yr = datetime.now().strftime("%Y")
    birp_user_id = "1217281510"
    # get latest birp playlists
    birp_pls = spotify.user_playlists(birp_user_id, limit=10)["items"]
    # find current playlist
    curr_birp_id = None
    for pl in birp_pls:
        if all(x in pl["name"] for x in ["BIRP!", mo, yr]):
            curr_birp_id = pl["id"]
            break
    # read tracks from current playlist
    curr_birp = spotify.user_playlist(birp_user_id, playlist_id=curr_birp_id)
    curr_birp_tracks = []
    for item in curr_birp["tracks"]["items"]:
        curr_birp_tracks += [item["track"]]
    return curr_birp_tracks


def track(spotify, title, artist='', limit=10):
    'search for track and attempt exact match'

    results = spotify.search(q=f'{title} {artist}', limit=limit, type='track')
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
