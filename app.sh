#!/bin/bash
set -e
source secrets/auth.sh
source .venv/bin/activate
export FLASK_APP=spotifytools.app
python -m flask run --port 9224 --host 0.0.0.0
