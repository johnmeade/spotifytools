
def heart(spotify, track):
    spotify.current_user_saved_tracks_add([track['uid']])
