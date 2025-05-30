'''
https://github.com/plamere/spotipy/pull/539
'''

from ..actions.queue import shuffle_liked_albums, shuffle_recent_liked, shuffle_recent_liked_and_birp

from flask import Flask, session, request, redirect, render_template
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
        return render_template("auth.html", auth_url=auth_url)

    # Step 4. Signed in, display data
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    return render_template("index.html", username=spotify.me()["display_name"])


@app.route('/sign_out')
def sign_out():
    os.remove(session_cache_path())
    session.clear()
    return redirect('/')


@app.route('/album_shuffle')
def album_shuffle_route():
    return _generic_route(shuffle_liked_albums, [], 'up to 25 random liked albums.')


@app.route('/shuffle_recent_liked')
def shuffle_recent_liked_route():
    return _generic_route(shuffle_recent_liked, [], 'shuffled recently liked songs.')


@app.route('/shuffle_recent_liked_and_birp')
def shuffle_recent_liked_and_birp_route():
    return _generic_route(shuffle_recent_liked_and_birp, [], 'shuffled recently liked songs and BIRP songs.')


def _generic_route(action, extra_args, resp_msg):
    auth_manager = session_auth_mgr()
    if not auth_manager.get_cached_token():
        return redirect('/')
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    Thread(target=action, args=[spotify] + extra_args).start()
    return render_template("success.html", description=resp_msg)
