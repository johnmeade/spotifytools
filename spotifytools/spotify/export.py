from .query import all_liked_tracks
import pickle


def saved_tracks(api, out_fn, verbose=False):
    # query
    print('Fetching all liked songs') if verbose else None
    liked = all_liked_tracks(api, pbar=verbose)
    # save
    print('Saving to disk') if verbose else None
    with open(out_fn, 'wb') as f:
        pickle.dump(liked, f)
