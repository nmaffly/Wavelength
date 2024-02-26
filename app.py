from flask import Flask, render_template, Flask, render_template, redirect, request, session
import spotipy
import os
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import json

app = Flask(__name__)


load_dotenv()

app.secret_key = os.getenv('FLASK_SECRET_KEY')
SPOTIPY_CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
SPOTIPY_CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET')
SPOTIPY_REDIRECT_URI = os.getenv('SPOTIPY_REDIRECT_URI')
SCOPE = 'user-library-read user-top-read user-read-currently-playing'

sp_oauth = SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET, redirect_uri=SPOTIPY_REDIRECT_URI, scope=SCOPE)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route('/callback')
def callback():
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    session['token_info'] = token_info
    return redirect('/display')


@app.route('/display')
def display():
    token_info = session.get('token_info', None)
    if not token_info:
        return redirect('/login')
    if sp_oauth.is_token_expired(token_info):
        token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
        session['token_info'] = token_info

    spotify = spotipy.Spotify(auth=token_info['access_token'])

    user_data = spotify.current_user()
    top_artists_r = spotify.current_user_top_artists(limit=10, time_range='short_term')['items']
    top_artists_a = spotify.current_user_top_artists(limit=10, time_range='long_term')['items']
    top_tracks_r = spotify.current_user_top_tracks(limit=10, time_range='short_term')['items']
    top_tracks_a = spotify.current_user_top_tracks(limit=10, time_range='long_term')['items']

    artist_genres_r = get_artist_genres(top_artists_r) # dictionary with top 10 artists and associated genre
    artists_r = list(artist_genres_r.keys())
    genres_r = get_genre_count(artist_genres_r)
    popularity_r = get_popularity(top_artists_r)
    tempo_r, loudness_r, acousticness_r, danceability_r, valence_r, energy_r, speechiness_r = get_audio_features_tracks(top_tracks_r, spotify)


    return render_template('index.html', user_data=user_data, artist_genres_r=artist_genres_r, genre__r=genres_r,popularity_r=popularity_r, artists_r=artists_r, tempo_r=tempo_r, loudness_r=loudness_r, acousticness_r=acousticness_r, danceability_r=danceability_r, valence_r=valence_r, energy_r=energy_r, speechiness_r=speechiness_r)

def get_artist_genres(top_artists):
    # returns dictionary with top 10 artists and associated genres, popularity scores, 
    # dictionary: (key, value) --> (artist, genres)
    artists = {}
    for item in top_artists:
        artists[item['name']] = item['genres']

    return artists

def get_genre_count(genres):
    # returns dictionary of genres and their respective count (calculated based on artists), sorted by count
    # dictionary: (key, value) --> (genre, count)
    all_genres = {}
    for artist, genres in genres.items():
        for genre in genres:
            if genre in all_genres.keys():
                count = all_genres[genre] 
                count += 1
                all_genres[genre] = count
            else:
                all_genres[genre] = 1
    
    all_genres = {k: v for k, v in sorted(all_genres.items(), key=lambda item: item[1], reverse=True)}
    
    return all_genres

def get_popularity(top_artists):
    # returns median popularity score for top 10 artists
    popularity_scores = []
    for item in top_artists:
        popularity_scores.append(item['popularity'])

    print(popularity_scores)

    median = find_median(popularity_scores)
    
    return median

def get_audio_features_tracks(top_tracks, spotify):
    # returns median tempo for top 10 artists
    tempo_scores = []
    loudness_scores = []
    acousticness_scores = []
    danceability_scores = []
    valence_scores = []
    energy_scores = []
    speechiness_scores = []
    
    for track in top_tracks:
        # print(artist['name'], end=':\n')
        tempo = 0
        loudness = 0
        acousticness = 0
        danceability = 0
        valence = 0
        energy = 0
        speechiness = 0

        if track:
            track_id = track['id']
            audio_features = spotify.audio_features([track_id])[0]
            if 'tempo' in audio_features:
                tempo = audio_features['tempo']

            if 'loudness' in audio_features:
                loudness += audio_features['loudness']

            if 'acousticness' in audio_features:
                #print(f"{track['name']} acousticness: {audio_features['acousticness']}")
                acousticness += audio_features['acousticness']

            if 'danceability' in audio_features:
                danceability += audio_features['danceability']

            if 'valence' in audio_features:
                valence += audio_features['valence']

            if 'energy' in audio_features:
                energy += audio_features['energy']
            
            if 'speechiness' in audio_features:
                speechiness += audio_features['speechiness']

            # print(f"{track['name']} tempo: {audio_features['tempo']}")
            # print(f"{track['name']} loudness: {audio_features['loudness']}")
        

        tempo_scores.append(tempo)
        loudness_scores.append(loudness)
        acousticness_scores.append(acousticness)
        danceability_scores.append(danceability)
        valence_scores.append(valence)
        energy_scores.append(energy)
        speechiness_scores.append(speechiness)

    median_tempo = round(find_median(tempo_scores),ndigits=2)
    median_loudness = round(find_median(loudness_scores),ndigits=2)
    median_acousticness = round(find_median(acousticness_scores), ndigits=2)
    median_danceability = round(find_median(danceability_scores), ndigits=2)
    median_valence = round(find_median(valence_scores), ndigits=2)
    median_energy = round(find_median(energy_scores), ndigits=2)
    median_speechiness = round(find_median(speechiness_scores), ndigits=2)
    
    return median_tempo, median_loudness, median_acousticness, median_danceability, median_valence, median_energy, median_speechiness

def get_audio_features_artists(top_artists, spotify):
    # returns median tempo for top 10 artists
    tempo_scores = []
    loudness_scores = []
    acousticness_scores = []
    danceability_scores = []
    valence_scores = []
    energy_scores = []
    speechiness_scores = []
    
    for artist in top_artists:
        top_tracks = spotify.artist_top_tracks(artist['id'], country='US')['tracks']
        # print(artist['name'], end=':\n')

        if top_tracks:
            avg_tempo = 0
            avg_loudness = 0
            avg_acousticness = 0
            avg_danceability = 0
            avg_valence = 0
            avg_energy = 0
            avg_speechiness = 0
            num_tracks = 0
            for track in top_tracks:
                track_id = track['id']
                audio_features = spotify.audio_features([track_id])[0]
                if audio_features['tempo']:
                    avg_tempo += audio_features['tempo']

                if audio_features['loudness']:
                    avg_loudness += audio_features['loudness']

                if 'acousticness' in audio_features:
                    #print(f"{track['name']} acousticness: {audio_features['acousticness']}")
                    avg_acousticness += audio_features['acousticness']

                if 'danceability' in audio_features:
                    avg_danceability += audio_features['danceability']

                if 'valence' in audio_features:
                    avg_valence += audio_features['valence']

                if 'energy' in audio_features:
                    avg_energy += audio_features['energy']
                
                if 'speechiness' in audio_features:
                    avg_speechiness += audio_features['speechiness']

                # print(f"{track['name']} tempo: {audio_features['tempo']}")
                # print(f"{track['name']} loudness: {audio_features['loudness']}")
                
                num_tracks += 1
            
            avg_tempo /= num_tracks
            avg_loudness /= num_tracks
            avg_acousticness /= num_tracks
            avg_danceability /= num_tracks
            avg_valence /= num_tracks
            avg_energy /= num_tracks
            avg_speechiness /= num_tracks
        

        tempo_scores.append(avg_tempo)
        loudness_scores.append(avg_loudness)
        acousticness_scores.append(avg_acousticness)
        danceability_scores.append(avg_danceability)
        valence_scores.append(avg_valence)
        energy_scores.append(avg_energy)
        speechiness_scores.append(avg_speechiness)

    median_tempo = round(find_median(tempo_scores),ndigits=2)
    median_loudness = round(find_median(loudness_scores),ndigits=2)
    median_acousticness = round(find_median(acousticness_scores), ndigits=2)
    median_danceability = round(find_median(danceability_scores), ndigits=2)
    median_valence = round(find_median(valence_scores), ndigits=2)
    median_energy = round(find_median(energy_scores), ndigits=2)
    median_speechiness = round(find_median(speechiness_scores), ndigits=2)
    
    return median_tempo, median_loudness, median_acousticness, median_danceability, median_valence, median_energy, median_speechiness

def find_median(numbers):
    numbers.sort()
    
    middle = len(numbers) // 2
    
    if len(numbers) % 2 != 0:
        return numbers[middle]
    else:
        return (numbers[middle - 1] + numbers[middle]) / 2.0

if __name__ == '__main__':
    app.run(debug=True, port=4000)


