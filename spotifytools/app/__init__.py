from ..actions.queue import shuffle_liked_albums

from flask import Flask, session, request, redirect
from flask_session import Session
import spotipy

from threading import Thread
from pathlib import Path
import os


HERE = Path(__file__).parent

# flask init
app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(64)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = str(HERE.joinpath('.session'))

# flask session init
Session(app)

# spotipy init
SCOPES = ','.join([
    'user-modify-playback-state',
    'user-library-read',
])
auth_manager = spotipy.oauth2.SpotifyOAuth(scope=SCOPES, cache_path=HERE.joinpath('.cache'))
spotify = spotipy.Spotify(auth_manager=auth_manager)


def perform(action, args):
    thread = Thread(target=action, args=args)
    thread.start()


@app.route('/')
def index():
    if request.args.get("code"):
        session['token_info'] = auth_manager.get_access_token(request.args["code"])
        return redirect('/')

    if not session.get('token_info'):
        auth_url = auth_manager.get_authorize_url()
        return f'<h2><a href="{auth_url}">Authorize with Spotify</a></h2>'

    return (
        f'<h2>Logged in as: {spotify.me()["display_name"]}  '
        f'<a href="/sign_out">[sign out]<a/></h2>'
        f'<a href="/album_shuffle">Shuffle my liked albums</a>'
    )


@app.route('/sign_out')
def sign_out():
    session.clear()
    return redirect('/')


@app.route('/album_shuffle')
def playlists():
    if not session.get('token_info'):
        return redirect('/')
    else:
        perform(shuffle_albums, (spotify,))
        return (
            '<p>You queue will shortly populate with up to 25 random liked albums.</p>'
            '<p>You can leave this page.</p>'
            '<a href="/">Home</a>'
        )
