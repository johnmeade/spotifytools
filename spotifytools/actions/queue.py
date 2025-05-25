from .query import get_liked_albums, get_liked_tracks, get_curr_birp_tracks
from random import sample, shuffle
from time import sleep


def shuffle_liked_albums(spotify, track_sleep=1.0, limit=25):
    albums = get_liked_albums(spotify)
    limit = min(len(albums), limit or len(albums))
    for album in sample(albums, k=limit):
        tracks = sorted(album['tracks']['items'], key=lambda t: t['track_number'])
        for track in tracks:
            spotify.add_to_queue(track['uri'])
            sleep(track_sleep)


def shuffle_recent_liked(spotify, track_sleep=1.0):
    tracks = get_liked_tracks(spotify, limit=100)
    shuffle(tracks)
    for track in tracks:
        spotify.add_to_queue(track['uri'])
        sleep(track_sleep)


def shuffle_recent_liked_and_birp(spotify, track_sleep=1.0):
    tracks = get_liked_tracks(spotify, limit=100)
    tracks += get_curr_birp_tracks(spotify)
    shuffle(tracks)
    for track in tracks:
        spotify.add_to_queue(track['uri'])
        sleep(track_sleep)
