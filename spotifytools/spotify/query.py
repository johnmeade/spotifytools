from time import sleep
from tqdm import tqdm


RATE_LIMIT_SLEEP = 0.1 # spotify API has strict limiting
MAX_LIMIT = 50


def _all_paginated_items(func, limit=None, pbar=False):
    items = []
    offset = 0
    total = 0
    progress = None
    while True:
        # obtain and read chunk
        chunk_limit = MAX_LIMIT if limit is None else min(MAX_LIMIT, limit - len(items))
        if chunk_limit <= 0:
            return items
        chunk = func(limit=chunk_limit, offset=offset)
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


def all_liked_albums(api, pbar=False):
    items = _all_paginated_items(api.current_user_saved_albums, pbar=pbar)
    return [ item['album'] for item in items ]


def all_liked_tracks(api, pbar=False):
    items = _all_paginated_items(api.current_user_saved_tracks, pbar=pbar)
    return [ item['track'] for item in items ]


def all_new_releases(api, limit=100, pbar=False):
    assert limit <= 1000
    items = _all_paginated_items(api.current_user_saved_tracks, limit, pbar)
    # return [ item['name'] for item in items ]
    import ipdb; ipdb.set_trace()
    return items


def batch_similar_artists(api, artists, pbar=False):
    if pbar:
        artists = tqdm(artists)

    similar = dict()
    for artist in artists:
        type_ = type(artist)
        if type_ == dict:
            assert 'uri' in artist, "artist dict has no uri"
            uri = artist['uri']
        elif type_ == str:
            exact, _ = exact_search(api, artist=artist)
            sleep(RATE_LIMIT_SLEEP)
            if exact is None:
                continue
            uri = exact['uri']
        else:
            import ipdb; ipdb.set_trace()
            raise ValueError("unknown artist object:", artist)

        # get similar
        sim = api.artist_related_artists(uri)
        sleep(RATE_LIMIT_SLEEP)
        similar.update({ a['uri']: a for a in sim['artists'] })

    return list(similar.values())


def exact_search(api, track=None, artist=None, album=None, limit=10):
    'search for track/artist/album and attempt exact match (case insensitive)'

    # unpack
    track = track.lower().strip() if track else None
    artist = artist.lower().strip() if artist else None
    album = album.lower().strip() if album else None
    q = ', '.join(filter(None, [track, artist, album]))
    type_ = 'track' if track is not None else 'artist' if artist is not None else 'album'

    # search
    results = api.search(q=q, limit=limit, type=type_)
    results = results[type_ + 's']['items']

    # check for exact match
    for result in results:

        # parse
        res_track, res_artists, res_album = None, None, None
        if type_ == 'track':
            res_track = result['name'].lower().strip()
            res_artists = [ a['name'].lower().strip() for a in result['artists'] ]
            res_album = result['album']['name'].lower().strip()

        elif type_ == 'artist':
            res_artists = [ result['name'].lower().strip() ]

        elif type_ == 'album':
            res_artists = [ a['name'].lower().strip() for a in result['artists'] ]
            res_album = result['name'].lower().strip()

        # match conditions
        if res_track and track and track != res_track: continue
        if res_artists and artist and not any(ra == artist for ra in res_artists): continue
        if res_album and album and res_album != album: continue

        return result, results

    return None, results
