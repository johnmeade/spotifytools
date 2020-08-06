
# Setup

Install:

```sh
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create authentication file:

```sh
# secrets/auth.sh
export SPOTIPY_CLIENT_ID=a1b2c3d4e5f6g7h8i9
export SPOTIPY_CLIENT_SECRET=a1b2c3d4e5f6g7h8i9
export SPOTIPY_REDIRECT_URI='http://localhost:1234'
```

Run scripts:

```sh
python -m spotifytools.scripts.save_liked
```

Run server:

```sh
./app.sh
```
