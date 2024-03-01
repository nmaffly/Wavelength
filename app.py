from flask import Flask, render_template, Flask, render_template, redirect, request, session, jsonify
import spotipy
import os
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
from extraction import get_artist_genres, get_genre_count, get_popularity, get_audio_features_tracks, get_audio_features_artists, get_variance


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
    return render_template('home.html')

@app.route('/login')
def login():
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route('/callback')
def callback():
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    session['token_info'] = token_info
    return render_template('loading.html')


@app.route('/fetch_data')
def fetch_data():
    token_info = session.get('token_info', None)
    if not token_info:
        return redirect('/login')
    if sp_oauth.is_token_expired(token_info):
        token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
        session['token_info'] = token_info

    spotify = spotipy.Spotify(auth=token_info['access_token'])

    # extracted user data
    user_data = spotify.current_user()
    
    # stored user data
    user_name = user_data['display_name']
    profile_pic = user_data['images'][1]['url']

    # extracted recent data 
    top_artists_r = spotify.current_user_top_artists(limit=50, time_range='short_term')['items']
    top_tracks_r = spotify.current_user_top_tracks(limit=50, time_range='short_term')['items']
    
    # extracted all time data
    top_artists_a = spotify.current_user_top_artists(limit=50, time_range='long_term')['items']
    top_tracks_a = spotify.current_user_top_tracks(limit=50, time_range='long_term')['items']

    # Recent stats
    artist_genres_r = get_artist_genres(top_artists_r) # dictionary with top 10 artists and associated genre
    artists_r = list(artist_genres_r.keys())
    genres_r = get_genre_count(artist_genres_r)
    popularity_r = get_popularity(top_artists_r)
    median_values_r = get_audio_features_tracks(top_tracks_r, spotify)
    variance_r = get_variance() 
    median_values_r.append(popularity_r)
    median_values_r.append(variance_r)

    #All Time stats
    artist_genres_a = get_artist_genres(top_artists_a) # dictionary with top 10 artists and associated genre
    artists_a = list(artist_genres_a.keys())
    genres_a = get_genre_count(artist_genres_a)
    popularity_a = get_popularity(top_artists_a)
    median_values_a = get_audio_features_tracks(top_tracks_a, spotify)
    variance_a = get_variance()
    median_values_a.append(popularity_a)
    median_values_a.append(variance_a)
    
    graph_json = {
        "median_values_r": median_values_r,
        "median_values_a": median_values_a,
    }

    session['processed_data'] = {
        "graph_json": graph_json,
        "median_values_r": median_values_r,
        "median_values_a": median_values_a,
        "user_data": user_data,
        "user_name": user_name,
        "profile_pic": profile_pic,
        "artist_genres_r": artist_genres_r,
        "genre_r": genres_r,
        "artists_r": artists_r,
        "artist_genres_a": artist_genres_a,
        "genre_a": genres_a,
        "artists_a": artists_a
    }
    return jsonify(success=True)

@app.route('/display')
def display():
    processed_data = session.get('processed_data', {})
    if not processed_data:
        return redirect('/login')  # or handle as appropriate
    return render_template('user_dashboard.html', **processed_data)
    
if __name__ == '__main__':
    app.run(debug=True, port=4000)


