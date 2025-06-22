'''
https://github.com/plamere/spotipy/pull/539
'''

from ..actions.queue import JOBS, shuffle_liked_albums, shuffle_recent_liked, shuffle_recent_liked_and_birp, john_shuffle

from flask import Flask, session, request, redirect, render_template
from flask_session import Session
import spotipy

from threading import Thread
from pathlib import Path
from secrets import token_hex
from uuid import uuid4
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


def get_uuid():
    if not session.get('uuid'):
        # Step 1. Visitor is unknown, give random ID
        session['uuid'] = str(uuid4())
    return session['uuid']


@app.route('/')
def index():
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


@app.route('/jobs', methods=["POST"])
def jobs_route():
    return dict(job_ids=list(JOBS[get_uuid()]))


@app.route('/stop_job', methods=["POST"])
def stop_job_route():
    jobs = JOBS[get_uuid()]
    job_id = request.args.get("job_id")
    msg = "Not found"
    if job_id in jobs:
        jobs.remove(job_id)
        msg = "Success"
    return dict(msg=msg)


@app.route('/album_shuffle', methods=["POST"])
def album_shuffle_route():
    return _generic_route(shuffle_liked_albums, 'Adding up to 25 random liked albums.')


@app.route('/shuffle_recent_liked', methods=["POST"])
def shuffle_recent_liked_route():
    return _generic_route(shuffle_recent_liked, 'Shuffling recently liked songs.')


@app.route('/shuffle_recent_liked_and_birp', methods=["POST"])
def shuffle_recent_liked_and_birp_route():
    return _generic_route(shuffle_recent_liked_and_birp, 'Shuffling recently liked songs and BIRP songs.')


@app.route('/john_birp_shuffle', methods=["POST"])
def john_birp_shuffle_route():
    return _generic_route(john_shuffle, 'Shuffling various John music + BIRP.', extra_kwargs=dict(incl_birp=True))


@app.route('/john_shuffle', methods=["POST"])
def john_shuffle_route():
    return _generic_route(john_shuffle, 'Shuffling various John music.', extra_kwargs=dict(incl_birp=False))


def _generic_route(action, resp_msg, extra_args=[], extra_kwargs=dict()):
    auth_manager = session_auth_mgr()
    if not auth_manager.get_cached_token():
        return redirect('/')
    job_id = token_hex(16)
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    Thread(target=action, args=[get_uuid(), job_id, spotify] + extra_args, kwargs=extra_kwargs).start()
    return dict(msg=resp_msg)
