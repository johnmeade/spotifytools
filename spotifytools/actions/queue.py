from .query import all_liked_albums
from random import sample
from time import sleep


def shuffle_liked_albums(spotify, track_sleep=1.0, limit=25):
    albums = all_liked_albums(spotify)
    limit = limit or len(albums)
    for album in sample(albums, k=limit):
        tracks = sorted(album['tracks']['items'], key=lambda t: t['track_number'])
        for track in tracks:
            spotify.add_to_queue(track['uri'])
            sleep(track_sleep)
