from flask import Flask, render_template, redirect, request, session, jsonify, url_for
import spotipy
import os
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
from extraction import get_artist_genres, get_genre_count, get_popularity, get_audio_features_tracks, get_variance
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_migrate import Migrate
from flask_session import Session
from database import User, UserStats, RecentGenres, AllTimeGenres, RecentArtists, AllTimeArtists, RecentTracks, AllTimeTracks, get_db_genres, get_db_artists, get_db_median_values, get_db_tracks, generate_sharing_token, db

app = Flask(__name__)

# Configure the Flask app to use Flask-Session
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY')
Session(app)  # Initialize the session

import os

app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{os.getenv("MYSQL_USER")}:{os.getenv("MYSQL_PASSWORD")}@{os.getenv("MYSQL_HOST")}/{os.getenv("MYSQL_DB")}'


db.init_app(app)
migrate = Migrate(app, db)

app.config['SESSION_TYPE'] = 'filesystem'
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY')
Session(app)  # Initialize the session

load_dotenv()

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
    cleanup()
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route('/callback')
def callback():
    code = request.args.get('code')
    cleanup()
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

    # Extracted and stored user data
    user_data = spotify.current_user()
    
    # check if user exists
    user = User.query.filter_by(spotify_id=user_data['id']).first()

    print("User acquired from database")

    if user:
        # If user exists, update tokens and most recent login
        # then pull stats from database into flask session

        user.access_token = token_info['access_token']
        user.refresh_token = token_info['refresh_token']
        user.token_expires_at = datetime.fromtimestamp(token_info['expires_at'])
        user.most_recent_login = datetime.utcnow()
    
        # pull spotify data from db and put into flask session
        median_values_r = get_db_median_values(user.id, 'r')
        median_values_a = get_db_median_values(user.id, 'a')

        session['processed_data'] = {
        "graph_json": {"median_values_r": median_values_r, "median_values_a": median_values_a},
        "median_values_r": median_values_r,
        "median_values_a": median_values_a,
        "user_data": user_data,
        "user_name": user.display_name,
        "profile_pic": user.profile_pic,
        "share_token": user.share_token,
        "genre_r": get_db_genres(user.id, 'r'),
        "genre_a": get_db_genres(user.id, 'a'),
        "artists_a": get_db_artists(user.id, 'a'),
        "artists_r": get_db_artists(user.id, 'r'),
        "tracks_r": get_db_tracks(user.id,'r'),
        "tracks_a": get_db_tracks(user.id,'a'),
        "popularity_r": median_values_r["popularity"],
        "tempo_r": median_values_r["tempo"],
        "loudness_r": median_values_r["loudness"],
        "acousticness_r": median_values_r["acousticness"],
        "danceability_r": median_values_r["danceability"],
        "valence_r": median_values_r["valence"],
        "energy_r": median_values_r["energy"],
        "speechiness_r": median_values_r["speechiness"],
        "variance_r": median_values_r["variance"]
    }

    else:
        # otherwise if it's a new user extract spotify info, add to database and session

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
        tracks_r = [track['name'] for track in top_tracks_r]
        popularity_r = get_popularity(top_artists_r)
        median_values_r = get_audio_features_tracks(top_tracks_r, spotify)
        variance_r = get_variance() 
        median_values_r.append(popularity_r)
        median_values_r.append(variance_r)

        #All Time stats
        artist_genres_a = get_artist_genres(top_artists_a) # dictionary with top 10 artists and associated genre
        artists_a = list(artist_genres_a.keys())
        genres_a = get_genre_count(artist_genres_a)
        tracks_a = [track['name'] for track in top_tracks_a]
        popularity_a = get_popularity(top_artists_a)
        median_values_a = get_audio_features_tracks(top_tracks_a, spotify)
        variance_a = get_variance()
        median_values_a.append(popularity_a)
        median_values_a.append(variance_a)

        # setting up db entry for new user
        user_share_token = generate_sharing_token()
        user = User(
            spotify_id=user_data['id'],
            display_name=user_data.get('display_name', 'No Name'),
            profile_pic=user_data['images'][0]['url'] if user_data['images'] else None,
            access_token=token_info['access_token'],
            refresh_token=token_info['refresh_token'],
            share_token=user_share_token,
            token_expires_at=datetime.fromtimestamp(token_info['expires_at'])
        )

        print("user instance made")
        db.session.add(user)
        try:
            db.session.commit()
            print("successfully commited to session")
        except Exception as e:
            # Handle database errors, such as connection issues or constraints violations
            print(f"Unable to commit to session: {e}")
            db.session.rollback()
            return jsonify(error=str(e)), 500
        
        print("user instanced added to db session")

        user_stats = UserStats(
            user_id=user.id,
            popularity_r=popularity_r,
            popularity_a=popularity_a,
            tempo_r=median_values_r[0],
            tempo_a=median_values_a[0],
            loudness_r=median_values_r[1],
            loudness_a=median_values_a[1],
            acousticness_r=median_values_r[2],
            acousticness_a=median_values_a[2],
            danceability_r=median_values_r[3],
            danceability_a=median_values_a[3],
            valence_r=median_values_r[4],
            valence_a=median_values_a[4],
            energy_r=median_values_r[5],
            energy_a=median_values_a[5],
            speechiness_r=median_values_r[6],
            speechiness_a=median_values_a[6],
            variance_r=variance_r,
            variance_a=variance_a
            )
        
        db.session.add(user_stats)
        try:
            db.session.commit()
            print("successfully commited to session")
        except Exception as e:
            # Handle database errors, such as connection issues or constraints violations
            print(f"Unable to commit to session: {e}")
            db.session.rollback()
            return jsonify(error=str(e)), 500
        print("User stats made and added to db session")

        for g, count in genres_r.items():
            new_genre = RecentGenres(
                user_stats_id=user_stats.id,
                genre=g,
                genre_count=count
            )
            db.session.add(new_genre)

        print("genres_r loaded in")
        
        for g, count in genres_a.items():
            new_genre = AllTimeGenres(
                user_stats_id=user_stats.id,
                genre=g,
                genre_count=count
            )
            db. session.add(new_genre)

        print("genres_a loaded in")

        for a in artists_r:
            new_artist = RecentArtists(
                user_stats_id=user_stats.id,
                artist=a
            )
            db.session.add(new_artist)
        
        for a in artists_a:
            new_artist = AllTimeArtists(
                user_stats_id=user_stats.id,
                artist=a
            )
            db. session.add(new_artist)
        
        print("artists loaded in")

        print(tracks_r)
        for track in tracks_r:
            new_track = RecentTracks(
                user_stats_id=user_stats.id,
                song=track
            )
            db.session.add(new_track)
        
        for track in tracks_a:
            new_track = AllTimeTracks(
                user_stats_id=user_stats.id,
                song=track
            )
            db. session.add(new_track)

        session['processed_data'] = {
        "graph_json": {"median_values_r": median_values_r, "median_values_a": median_values_a},
        "median_values_r": median_values_r,
        "median_values_a": median_values_a,
        "user_data": user_data,
        "user_name": user_name,
        "profile_pic": profile_pic,
        "share_token": user_share_token,
        "genre_r": genres_r,
        "genre_a": genres_a,
        "artists_a": artists_a,
        "artists_r": artists_r,
        "tracks_r": tracks_r,
        "tracks_a": tracks_a,
        "popularity_r": popularity_r,
        "tempo_r": median_values_r[0],
        "loudness_r": median_values_r[1],
        "acousticness_r": median_values_r[2],
        "danceability_r": median_values_r[3],
        "valence_r": median_values_r[4],
        "energy_r": median_values_r[5],
        "speechiness_r": median_values_r[6],
        "variance_r": variance_r,
    }

    try:
        db.session.commit()
        print("successfully commited to session")
    except Exception as e:
        # Handle database errors, such as connection issues or constraints violations
        print(f"Unable to commit to session: {e}")
        db.session.rollback()
        return redirect(url_for('error_page'))

    # print(session['processed_data'])
    return jsonify(success=True)

def cleanup():
    cache_file = '.cache'
    if os.path.exists(cache_file):
        os.remove(cache_file)

@app.route('/display')
def display():
    processed_data = session.get('processed_data', {})
    if not processed_data:
        return redirect('/login')
    return render_template('user_dashboard.html', **processed_data)

@app.route('/comparison')
def comparison():
    return render_template('comparison.html')

@app.route('/error')
def error_page():
    return render_template('error.html')

if __name__ == '__main__':
    app.run(debug=True, port=4000)
