from time import time, sleep
from datetime import datetime
from pathlib import Path

import json
from tqdm import tqdm


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


def get_playlist_tracks(spotify, name=None, pid=None):
    pls = spotify.current_user_playlists()
    for pl in pls["items"]:
        if (pid and pl["id"] == pid) or (name and pl["name"] == name):
            pl_detail = spotify.user_playlist(pl["owner"]["id"], playlist_id=pl["id"])
            return pl_detail["tracks"]["items"]
    print(f"ERROR: playlist not found ({name=}, {pid=})")
    return []


def get_john_variety_tracks(spotify):
    pl_detail = spotify.user_playlist("songlistener1998", playlist_id="7uAVNyIOCtftTU4J6xHvld")
    return pl_detail["tracks"]["items"]


_john_liked_cache_root = Path(__file__).parent.parent.parent / "cache" / "john_liked"
def get_cached_liked_tracks(spotify):
    global _john_liked_cache_root
    _john_liked_cache_root.mkdir(exist_ok=True)
    now = int(time() * 1000)

    # find all cache files (oldest-to-newest)
    cache_fps = sorted(list(_john_liked_cache_root.glob("[0-9]*.json")), key=lambda s: int(s.stem))

    # remove old files
    for fp in cache_fps[:-3]:
        fp.unlink()

    if len(cache_fps) == 0:
        # get all and cache
        cache = get_liked_tracks(spotify, limit=None)
        most_recent_fp = _john_liked_cache_root / f"{now}.json"
        most_recent_fp.write_text(json.dumps(cache))
    else:
        # read most recent
        most_recent_fp = cache_fps[-1]
        cache = json.loads(most_recent_fp.read_text())

        # check for updates TODO: handle more than 100 stale
        cache_ids = {track["id"] for track in cache}
        updates = get_liked_tracks(spotify, limit=100)
        added = 0
        for track in reversed(updates):
            if track["id"] not in cache_ids:
                cache = [track] + cache
                added += 1

        # update cache if it was changed
        if added > 0:
            most_recent_fp = _john_liked_cache_root / f"{now + 1}.json"
            most_recent_fp.write_text(json.dumps(cache))

    return cache


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
