#!/bin/bash
set -e
source secrets/auth.sh
export FLASK_APP=spotifytools.app
python -m flask run --port 9224 --host 0.0.0.0
