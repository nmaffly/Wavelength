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
    artist_genres_r = get_artist_genres(spotify) # dictionary with top 10 artists and associated genre
    genres_r = get_genre_count(artist_genres_r)

    popularity_r = get_popularity_r(spotify)

    artists_r = list(artist_genres_r.keys())

    genres_a = get_all_time(spotify)
    genre_count_a = get_genre_count(genres_a)

        

    return render_template('index.html', user_data=user_data, artist_genres_r=artist_genres_r, genre__r=genres_r, genres_a=genres_a, genre_count_a=genre_count_a, popularity_r=popularity_r, artists_r=artists_r)

def get_artist_genres(spotify):
    # returns dictionary with top 10 artists and associated genres, popularity scores, 
    # dictionary: (key, value) --> (artist, genres)
    artists = {}
    top_artists = spotify.current_user_top_artists(limit=10, time_range='short_term')['items']
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

def get_popularity_r(spotify):
    # returns nested dictionary with top 10 artists and associated genres, popularity scores, 
    # dictionary: (key, value) --> (artist, genres)
    popularity_scores = []
    top_artists = spotify.current_user_top_artists(limit=10, time_range='short_term')['items']
    for item in top_artists:
        popularity_scores.append(item['popularity'])

    print(popularity_scores)

    median = find_median(popularity_scores)
    
    return median

def find_median(numbers):
    numbers.sort()
    
    middle = len(numbers) // 2
    
    if len(numbers) % 2 != 0:
        return numbers[middle]
    else:
        return (numbers[middle - 1] + numbers[middle]) / 2.0

def get_medium(spotify):
    artists = {}
    top_artists = spotify.current_user_top_artists(limit=10, time_range='medium_term')['items']
    for item in top_artists:
        artists[item['name']] = item['genres']
    
    return artists

def get_all_time(spotify):
    artists = {}
    top_artists = spotify.current_user_top_artists(limit=10, time_range='long_term')['items']
    for item in top_artists:
        artists[item['name']] = item['genres']
    
    return artists




if __name__ == '__main__':
    app.run(debug=True, port=4000)


