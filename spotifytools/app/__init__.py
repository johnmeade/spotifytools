'''
https://github.com/plamere/spotipy/pull/539
'''

from ..actions.queue import JOBS, shuffle_liked_albums, shuffle_recent_liked, shuffle_recent_liked_and_birp, john_shuffle

from flask import Flask, session, request, redirect, render_template, abort
from flask_session import Session
from werkzeug.middleware.proxy_fix import ProxyFix
import spotipy

from threading import Thread
from pathlib import Path
from secrets import token_hex
from uuid import uuid4
import os


HERE = Path(__file__).parent

# flask init
app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
app.config['SECRET_KEY'] = os.urandom(64)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = str(HERE.joinpath('.session'))
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
Session(app)

# spotipy init
CACHE_ROOT = HERE.joinpath('.spotipy-cache').relative_to(Path.cwd())
SCOPES = ','.join([
    'user-modify-playback-state',
    'user-library-read',
    'playlist-read-private',
])


def get_uuid():
    if not session.get('uuid'):
        session['uuid'] = str(uuid4())
    return session['uuid']


def session_cache_path():
    return str(CACHE_ROOT.joinpath(get_uuid()))


def session_auth_mgr(show_dialog=False, state=None):
    return spotipy.oauth2.SpotifyOAuth(
        scope=SCOPES,
        cache_path=session_cache_path(),
        show_dialog=show_dialog,
        state=state,
    )


@app.route('/')
def index():
    if request.args.get("code"):
        # Step 3. Being redirected from Spotify auth page. Verify the state
        # we handed out in step 2 comes back unchanged (CSRF protection).
        expected_state = session.pop("oauth_state", None)
        if not expected_state or request.args.get("state") != expected_state:
            abort(400, "Invalid or missing OAuth state")
        auth_manager = session_auth_mgr(state=expected_state)
        auth_manager.get_access_token(request.args.get("code"))
        return redirect("/")

    auth_manager = session_auth_mgr(show_dialog=True)
    if not auth_manager.get_cached_token():
        # Step 2. Display authorize link when no token
        state = token_hex(16)
        session["oauth_state"] = state
        auth_url = auth_manager.get_authorize_url(state=state)
        return render_template("auth.html", auth_url=auth_url)

    # Step 4. Signed in, display data
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    return render_template(
        "index.html",
        username=spotify.me()["display_name"],
    )


@app.route('/sign_out')
def sign_out():
    os.remove(session_cache_path())
    session.clear()
    return redirect("/")


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
        return redirect("/")
    job_id = token_hex(16)
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    Thread(target=action, args=[get_uuid(), job_id, spotify] + extra_args, kwargs=extra_kwargs).start()
    return dict(msg=resp_msg)
