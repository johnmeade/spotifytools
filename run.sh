#!/bin/bash
set -e
source secrets/auth.sh
export SPOTIPY_REDIRECT_URI=${SPOTIPY_REDIRECT_URI:-"https://spotify.hbar.ca"}
echo "SPOTIPY_REDIRECT_URI: $SPOTIPY_REDIRECT_URI"

## dev
# export FLASK_APP=spotifytools.app
# python -m flask run --port 9224 --host 0.0.0.0

## prod
# tmux kill-session sends SIGHUP, which gunicorn treats as "reload workers", not
# "shut down" -- it survives as an orphan still holding the port. To actually
# stop this, send SIGTERM to the gunicorn arbiter PID instead.
gunicorn -b 0.0.0.0:9224 spotifytools.app:app --workers 1
