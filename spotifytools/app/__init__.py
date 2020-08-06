'''
https://github.com/plamere/spotipy/pull/539
'''

from ..actions.queue import shuffle_liked_albums

from flask import Flask, session, request, redirect
from flask_session import Session
import spotipy

from threading import Thread
from pathlib import Path
import uuid
import os


HERE = Path(__file__).parent

# flask init
app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(64)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = str(HERE.joinpath('.session'))
Session(app)

# spotipy init
CACHE_ROOT = HERE.joinpath('.spotipy-cache').relative_to(Path.cwd())
SCOPES = ','.join([
    'user-modify-playback-state',
    'user-library-read',
])


def session_cache_path():
    return str(CACHE_ROOT.joinpath(session.get('uuid')))


def session_auth_mgr(show_dialog=False):
    return spotipy.oauth2.SpotifyOAuth(
        scope=SCOPES,
        cache_path=session_cache_path(),
        show_dialog=True,
    )


@app.route('/')
def index():
    if not session.get('uuid'):
        # Step 1. Visitor is unknown, give random ID
        session['uuid'] = str(uuid.uuid4())

    auth_manager = session_auth_mgr(show_dialog=True)
    if request.args.get("code"):
        # Step 3. Being redirected from Spotify auth page
        auth_manager.get_access_token(request.args.get("code"))
        return redirect('/')

    if not auth_manager.get_cached_token():
        # Step 2. Display authorize link when no token
        auth_url = auth_manager.get_authorize_url()
        return f'<h2><a href="{auth_url}">Authorize with Spotify</a></h2>'

    # Step 4. Signed in, display data
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    return (
        f'<h2>Logged in as: {spotify.me()["display_name"]}  '
        f'<a href="/sign_out">[sign out]<a/></h2>'
        f'<a href="/album_shuffle">Shuffle my liked albums</a>'
    )


@app.route('/sign_out')
def sign_out():
    os.remove(session_cache_path())
    session.clear()
    return redirect('/')


@app.route('/album_shuffle')
def album_shuffle():
    auth_manager = session_auth_mgr()
    if not auth_manager.get_cached_token():
        return redirect('/')

    spotify = spotipy.Spotify(auth_manager=auth_manager)
    Thread(target=shuffle_liked_albums, args=(spotify,)).start()
    return (
        '<p>You queue will shortly populate with up to 25 random liked albums.</p>'
        '<p>You can leave this page.</p>'
        '<a href="/">Home</a>'
    )
