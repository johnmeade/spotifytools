import spotipy
from pathlib import Path

_APP_CACHE_DIR = Path(__file__).parents[1] / 'app' / '.spotipy-cache'


def get_api(scope='user-library-read'):
    # Reuse the most recently touched token from the Flask app session cache.
    # Log in via the web app first if this fails.
    caches = sorted(_APP_CACHE_DIR.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True)
    if not caches:
        raise RuntimeError('No cached auth found — log in via the web app first.')
    return spotipy.Spotify(auth_manager=spotipy.oauth2.SpotifyOAuth(
        scope=scope,
        cache_path=str(caches[0]),
    ))
