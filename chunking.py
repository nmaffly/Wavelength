import time
import spotipy
from extraction import get_artist_genres, get_genre_count, get_popularity, get_audio_features_tracks, get_audio_features_artists, get_variance
import requests

def get_audio_features_tracks(spotify, track_ids):
    chunk_size = 10
    all_features = []
    for i in range(0, sum(map(len, track_ids)), chunk_size):
        chunk = track_ids[i:i+chunk_size]
        done = False
        while not done:
            try:
                print(f"Chunk content: {chunk}")
                features = spotify.audio_features(chunk)
                all_features.extend(features)
                done = True
            except spotipy.exceptions.SpotifyException as e:
                if e.http_status == 429:
                    retry_after = int(e.headers.get('Retry-After', 1))
                    print(f"Rate limited. Retrying after {retry_after} seconds.")
                    time.sleep(retry_after + 1)
                else:
                    raise e
    return all_features
