#!/bin/bash
set -e
source secrets/auth.sh
export SPOTIFYTOOLS_ROOT_PATH_PREFIX=${SPOTIFYTOOLS_ROOT_PATH_PREFIX:-'spotifytools'}
export SPOTIPY_REDIRECT_URI=${SPOTIPY_REDIRECT_URI:-"https://hbar.ca/$SPOTIFYTOOLS_ROOT_PATH_PREFIX"}

echo "SPOTIPY_REDIRECT_URI: $SPOTIPY_REDIRECT_URI"

## dev
# export FLASK_APP=spotifytools.app
# python -m flask run --port 9224 --host 0.0.0.0

## prod
gunicorn -b 0.0.0.0:9224 spotifytools.app:app
