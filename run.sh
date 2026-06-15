#!/bin/bash
set -e
source secrets/auth.sh
export SPOTIPY_REDIRECT_URI=${SPOTIPY_REDIRECT_URI:-"https://spotify.hbar.ca"}
echo "SPOTIPY_REDIRECT_URI: $SPOTIPY_REDIRECT_URI"

## dev
# export FLASK_APP=spotifytools.app
# python -m flask run --port 9224 --host 0.0.0.0

## prod
gunicorn -b 0.0.0.0:9224 spotifytools.app:app --workers 1
