"""
TODO API call
"""

import pickle
from pathlib import Path

import spotipy
from tqdm import tqdm

from ..scrape.aoty import new_releases
from ..spotify import export, query


HERE = Path(__file__).parent
SAVED_TRACK_PKL = HERE.joinpath('.artifacts', 'saved_tracks.pkl')


def main():
    # spotipy init
    auth_manager = spotipy.oauth2.SpotifyOAuth(scope='user-library-read', cache_path='/tmp/spotipy')
    api = spotipy.Spotify(auth_manager=auth_manager)

    if not SAVED_TRACK_PKL.exists():
        export.saved_tracks(api, SAVED_TRACK_PKL, verbose=True)

    with SAVED_TRACK_PKL.open('rb') as f:
        saved = pickle.load(f)

    saved_artists = dict()
    for track in saved:
        saved_artists.update({ a['uri']: a for a in track['artists'] })

    print('Scraping new releases')
    releases = new_releases(pbar=True)

    print('Searching new release artists')
    release_artists = [ query.exact_search(api, artist=r['artist'])[0] for r in tqdm(releases) ]
    release_artists = [ ra for ra in release_artists if ra ]

    print('Searching new release albums')
    release_links = [ query.exact_search(api, album=r['album'])[0] for r in tqdm(releases) ]
    release_links = [ l['external_urls']['spotify'] if l else l for l in release_links ]

    print('Finding similar artists')
    similar_artists = query.batch_similar_artists(api, release_artists, pbar=True)
    similar_artists = { a['uri']: a for a in similar_artists }
    similar_artists = { k: v for k, v in similar_artists.items() if k not in saved_artists }

    print('Matching to saved tracks')
    return dict(
        primary=[
            {'link': link, **release}
            for release, artist, link in zip(releases, release_artists, release_links)
            if artist['uri'] in saved_artists
        ],
        secondary=[
            {'link': link, **release}
            for release, artist, link in zip(releases, release_artists, release_links)
            if artist['uri'] in similar_artists
        ],
    )


if __name__ == '__main__':
    rec = main()
    print('From artists you like:')
    for rel in rec['primary']:
        print('\n'.join([
            f'',
            f'  Artist: {rel["artist"]}',
            f'  Album: {rel["album"]}',
            f'  Date: {rel["date"]}',
            f'  Link: {rel["link"]}',
            f'',
        ]))
    print('Other recommendations:')
    for rel in rec['secondary']:
        print('\n'.join([
            f'',
            f'  Artist: {rel["artist"]}',
            f'  Album: {rel["album"]}',
            f'  Date: {rel["date"]}',
            f'  Link: {rel["link"]}',
            f'',
        ]))
