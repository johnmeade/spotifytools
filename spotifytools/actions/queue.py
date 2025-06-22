from .query import (
    get_liked_albums, get_liked_tracks, get_curr_birp_tracks, get_john_variety_tracks, get_cached_liked_tracks,
)
from spotipy.exceptions import SpotifyException
from collections import defaultdict
from random import sample, shuffle
from time import sleep


# (this won't work with multi-proc)
JOBS = defaultdict(set) # session uuid => job set
TRACK_SLEEP=0.5


def _add_tracks(uuid, job_id, spotify, tracks, track_sleep):
    jobset = JOBS[uuid]
    jobset.add(job_id)

    for track in tracks:
        try:
            spotify.add_to_queue(track['uri'])
        except SpotifyException:
            print(f"ERROR adding track {track}")
            pass
        sleep(track_sleep)
        if job_id not in jobset:
            return

    if job_id in jobset:
        jobset.remove(job_id)


def shuffle_liked_albums(uuid, job_id, spotify, track_sleep=TRACK_SLEEP, limit=25):
    albums = get_liked_albums(spotify)
    limit = min(len(albums), limit or len(albums))
    tracks = []
    for album in sample(albums, k=limit):
        tracks += sorted(album['tracks']['items'], key=lambda t: t['track_number'])
    _add_tracks(uuid, job_id, spotify, tracks, track_sleep)


def shuffle_recent_liked(uuid, job_id, spotify, track_sleep=TRACK_SLEEP):
    tracks = get_liked_tracks(spotify, limit=100)
    shuffle(tracks)
    _add_tracks(uuid, job_id, spotify, tracks, track_sleep)


def shuffle_recent_liked_and_birp(uuid, job_id, spotify, track_sleep=TRACK_SLEEP):
    tracks = get_liked_tracks(spotify, limit=100)
    tracks += get_curr_birp_tracks(spotify)
    shuffle(tracks)
    _add_tracks(uuid, job_id, spotify, tracks, track_sleep)


def john_shuffle(uuid, job_id, spotify, incl_birp=True, track_sleep=TRACK_SLEEP):
    # query tracks
    all_liked = get_cached_liked_tracks(spotify)
    recent_liked = all_liked[:50]
    variety = get_john_variety_tracks(spotify)
    birp = get_curr_birp_tracks(spotify) if incl_birp else []

    # shuffle and combine
    shuffle(all_liked)
    shuffle(recent_liked)
    shuffle(variety)
    shuffle(birp)
    tracks = all_liked[:50] + recent_liked + variety[:50] + birp[:50]
    shuffle(tracks)

    # add to queue
    _add_tracks(uuid, job_id, spotify, tracks, track_sleep)
