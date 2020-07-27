from threading import Thread
from random import shuffle
from time import sleep


RATE_LIMIT_SLEEP = 0.1
MAX_LIMIT = 50


def perform(action, args):
    thread = Thread(target=action, args=args)
    thread.start()


def get_all_paginated_items(func):
    items = []
    offset = 0
    total = 0
    while True:
        chunk = func(limit=MAX_LIMIT, offset=offset)
        total = chunk['total']
        chunk_items = chunk['items']
        items += chunk_items
        offset += len(chunk_items)
        if offset >= total:
            break
        sleep(RATE_LIMIT_SLEEP)
    return items


def get_liked_albums(spotify):
    items = get_all_paginated_items(spotify.current_user_saved_albums)
    return [ item['album'] for item in items ]


def shuffle_albums(spotify):
    albums = get_liked_albums(spotify)
    shuffle(albums)
    for album in albums[:25]:
        from operator import getitem
        tracks = sorted(album['tracks']['items'], key=lambda t: t['track_number'])
        for track in tracks:
            spotify.add_to_queue(track['uri'])
            sleep(1)
