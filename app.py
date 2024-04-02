from flask import Flask, render_template, redirect, request, session, jsonify, url_for
import spotipy
import os
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
from extraction import get_tracks_info, get_tracks_info_batch, get_artists_info, get_artist_genres_batch, get_artist_genres_batch, get_genre_count, get_genre_count_batch, get_popularity, get_audio_features_tracks, get_variance
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from flask_migrate import Migrate
from flask_session import Session
from database import User, UserStats, RecentGenres, AllTimeGenres, RecentArtists, AllTimeArtists, RecentTracks, AllTimeTracks, get_db_genres, get_db_artists, get_db_median_values, get_db_tracks, generate_sharing_token, load_user_stats, db
from urllib.parse import urlparse

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
sp = spotipy.Spotify(auth_manager=sp_oauth)

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/login')
def login():
    cleanup()
    auth_url = sp_oauth.get_authorize_url() #I'm trying to think abt how we can get around the max user issue and I think it might require giving
                                            #people unique IDs associated with whoever's account they're using (ie. Sean's, Nathan's, etc.) and then
                                            #having them plug that in before they sign in so that we can change the env variables and connect them
                                            #to the right account. Otherwise we will be stuck at 25. Might be too problematic, we'll have to test
    return redirect(auth_url)

@app.route('/callback')
def callback():
    code = request.args.get('code')
    cleanup()
    token_info = sp_oauth.get_access_token(code)
    session['token_info'] = token_info
    if not token_info:
        return redirect('/login')
    if sp_oauth.is_token_expired(token_info):
        token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
        session['token_info'] = token_info
    spotify = spotipy.Spotify(auth=token_info['access_token'])
    user_data = spotify.current_user()
    user = User.query.filter_by(spotify_id=user_data['id']).first()

    new_user = False
    if user:
        new_user = True
    return render_template('loading.html', new_user = new_user)

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
    print("Here_fetched")
    # check if user exists
    user = User.query.filter_by(spotify_id=user_data['id']).first()

    print("User acquired from database")

    if not user.last_updated:
        user.last_updated = user.created_at
    
    
    update_time_range = timedelta(weeks=1)

    # For immediate spotify updates (testing purposes), uncomment line below
    update_time_range = timedelta(seconds=1)

    if user and (datetime.utcnow() - user.last_updated) < update_time_range: #I changed this just to work on things
        # If user exists and it's been less than a week, update tokens and most recent login
        # then pull stats from database into flask session

        print("It's been less than 30 seconds. No data update")

        user.access_token = token_info['access_token']
        user.refresh_token = token_info['refresh_token']
        user.token_expires_at = datetime.fromtimestamp(token_info['expires_at'])
        user.most_recent_login = datetime.utcnow()
    
        # pull spotify data from db and put into flask session
        median_values_r = get_db_median_values(user.id, 'r')
        median_values_m = get_db_median_values(user.id, 'm')
        median_values_a = get_db_median_values(user.id, 'a')

        session['processed_data'] = {
        "graph_json": {
            "median_values_r": median_values_r, 
            "median_values_m": median_values_m, 
            "median_values_a": median_values_a
        },
        "median_values_r": median_values_r,
        "median_values_m": median_values_m, 
        "median_values_a": median_values_a,
        "user_data": user_data,
        "user_name": user.display_name,
        "profile_pic": user.profile_pic,
        "share_token": user.share_token,
        "genre_r": get_db_genres(user.id, 'r'),
        "genre_m": get_db_genres(user.id, 'm'),
        "genre_a": get_db_genres(user.id, 'a'),
        "artists_a": get_db_artists(user.id, 'a'),
        "artists_m": get_db_artists(user.id, 'm'),
        "artists_r": get_db_artists(user.id, 'r'),
        "tracks_r": get_db_tracks(user.id,'r'),
        "tracks_m": get_db_tracks(user.id, 'm'),
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
        # otherwise extract spotify info, add to database and session
        print("User doesn't exist, or it's been longer than 30 seconds, new data being pulled")
        # stored user data
        user_name = user_data['display_name']
        profile_pic = user_data['images'][1]['url']

        # extracted recent data 
        top_artists_r = spotify.current_user_top_artists(limit=20, time_range='short_term')['items']
        top_tracks_r = spotify.current_user_top_tracks(limit=50, time_range='short_term')['items']

        # extracted all time data
        top_artists_m = spotify.current_user_top_artists(limit=20, time_range='medium_term')['items']
        top_tracks_m = spotify.current_user_top_tracks(limit=50, time_range='medium_term')['items']
        
        # extracted all time data
        top_artists_a = spotify.current_user_top_artists(limit=20, time_range='long_term')['items']
        top_tracks_a = spotify.current_user_top_tracks(limit=50, time_range='long_term')['items']

        # Recent (1 month) stats
        artists_info_r = get_artists_info(top_artists_r) # dictionary with top artists and associated info
        artists_r = list(artists_info_r.keys())
        genres_r = get_genre_count(artists_info_r)
        tracks_r = get_tracks_info(top_tracks_r)
        popularity_r = get_popularity(top_artists_r)
        median_values_r = get_audio_features_tracks(tracks_r, spotify)
        variance_r = get_variance() 
        median_values_r['popularity'] = popularity_r
        median_values_r['variance'] = variance_r

        # Medium term (6 months) stats
        artists_info_m = get_artists_info(top_artists_m) # dictionary with top artists and associated info
        artists_m = list(artists_info_m.keys())
        genres_m = get_genre_count(artists_info_m)
        tracks_m = get_tracks_info(top_tracks_m)
        popularity_m = get_popularity(top_artists_m)
        median_values_m = get_audio_features_tracks(tracks_m, spotify)
        variance_m = get_variance()
        median_values_m['popularity'] = popularity_m
        median_values_m['variance'] = variance_m

        # All Time stats
        artists_info_a = get_artists_info(top_artists_a) # dictionary with top artists and associated info
        artists_a = list(artists_info_a.keys())
        genres_a = get_genre_count(artists_info_a)
        tracks_a = get_tracks_info(top_tracks_a)
        popularity_a = get_popularity(top_artists_a)
        median_values_a = get_audio_features_tracks(tracks_a, spotify)
        variance_a = get_variance()
        median_values_a['popularity'] = popularity_a
        median_values_a['variance'] = variance_a

        new_data = {
                "recent_genres": genres_r,
                "medium_genres": genres_m,
                "all_time_genres": genres_a,
                "recent_artists": artists_info_r,
                "medium_artists": artists_info_m,
                "all_time_artists": artists_info_a,
                "recent_tracks": tracks_r,
                "medium_tracks": tracks_m,
                "all_time_tracks": tracks_a
        }

        if not user:
            #if the user doesn't exist, create new user
            # setting up db entry for new user
            user_share_token = generate_sharing_token()
            user = User(
                spotify_id=user_data['id'],
                display_name=user_data.get('display_name', 'No Name'),
                profile_pic=user_data['images'][0]['url'] if user_data['images'] else None,
                access_token=token_info['access_token'],
                refresh_token=token_info['refresh_token'],
                share_token=user_share_token,
                token_expires_at=datetime.fromtimestamp(token_info['expires_at']),
                last_updated=datetime.utcnow(),
                most_recent_login = datetime.utcnow(),
                created_at=datetime.utcnow()
            )

            print("user instance made")
            db.session.add(user)
            try:
                db.session.commit()
            except Exception as e:
                # Handle database errors, such as connection issues or constraints violations
                print(f"Unable to commit to session: {e}")
                db.session.rollback()
                return jsonify(error=str(e)), 500
            
            print("user instanced added to db session")
            
            load_user_stats(user.id, median_values_r,median_values_m, median_values_a, new_data, update=False)
        else:
            # the user exists, update info in db
            user.last_updated = datetime.utcnow()
            user.most_recent_login = datetime.utcnow()
            load_user_stats(user.id, median_values_r, median_values_m, median_values_a, new_data, update=True)
            
        session['processed_data'] = {
            "graph_json": {
                "median_values_r": median_values_r,
                "median_values_m": median_values_m, 
                "median_values_a": median_values_a
            },
            "median_values_r": median_values_r,
            "median_values_m": median_values_m,
            "median_values_a": median_values_a,
            "user_data": user_data,
            "user_name": user_name,
            "profile_pic": profile_pic,
            "share_token": user.share_token,
            "genre_r": genres_r,
            "genre_m": genres_m,
            "genre_a": genres_a,
            "artists_a": artists_info_a,
            "artists_m": artists_info_m,
            "artists_r": artists_info_r,
            "tracks_r": tracks_r,
            "tracks_m": tracks_m,
            "tracks_a": tracks_a,
            "popularity_r": popularity_r,
            "tempo_r": median_values_r['tempo'],
            "loudness_r": median_values_r['loudness'],
            "acousticness_r": median_values_r['acousticness'],
            "danceability_r": median_values_r['danceability'],
            "valence_r": median_values_r['valence'],
            "energy_r": median_values_r['energy'],
            "speechiness_r": median_values_r['speechiness'],
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
def comparison_form():
    return render_template('compare_form.html')

@app.route('/compare/<user1_share_token>/<user2_share_token>')
def compare_users(user1_share_token, user2_share_token):
    # Compare two users based on their share tokens.
    
    # Fetch users by share token
    user1 = User.query.filter_by(share_token=user1_share_token).first()
    user2 = User.query.filter_by(share_token=user2_share_token).first()

    if not user1 or not user2:
        return jsonify({"error": "One or both users not found"}), 404

    # Fetch genres and artists using the users' database IDs
    user1_genres = set(get_db_genres(user1.id, 'a'))  # Assuming 'a' for all-time
    user2_genres = set(get_db_genres(user2.id, 'a'))

    user1_artists = set(get_db_artists(user1.id, 'a'))
    user2_artists = set(get_db_artists(user2.id, 'a'))

    # Find the intersection
    common_genres = user1_genres.intersection(user2_genres)
    common_artists = user1_artists.intersection(user2_artists)

    return render_template('comparison.html', common_genres=common_genres, common_artists=common_artists, user1_token=user1_share_token, user2_token=user2_share_token)

@app.route('/compare_form')
def compare_form():
    # Render the form for comparing two Spotify users by share tokens.
    return render_template('compare_form.html')

def get_graph_data(user_id):
    user_stats = UserStats.query.filter_by(user_id=user_id).first()
    if not user_stats:
        return None
    graph_data_all_time = {
        'acousticness': user_stats.acousticness_a,
        'danceability': user_stats.danceability_a,
        'energy': user_stats.energy_a,
        'loudness': user_stats.loudness_a,
        'speechiness': user_stats.speechiness_a,
        'popularity': user_stats.popularity_a,
        'speechiness': user_stats.speechiness_a,
        'tempo': user_stats.tempo_a,
        'valence': user_stats.valence_a
    }
    graph_data_recent = {
        'acousticness': user_stats.acousticness_r,
        'danceability': user_stats.danceability_r,
        'energy': user_stats.energy_r,
        'loudness': user_stats.loudness_r,
        'speechiness': user_stats.speechiness_r,
        'popularity': user_stats.popularity_r,
        'speechiness': user_stats.speechiness_r,
        'tempo': user_stats.tempo_r,
        'valence': user_stats.valence_r
    }
    return graph_data_all_time, graph_data_recent

@app.route('/comparison/<user1_share_token>/<user2_share_token>')
def comparison(user1_share_token, user2_share_token):
    user1 = User.query.filter_by(share_token=user1_share_token).first()
    user2 = User.query.filter_by(share_token=user2_share_token).first()
    if not user1 or not user2:
        return jsonify({"error": "One or both users not found"}), 404
    user1_graph_data_all_time, user1_graph_data_recent = get_graph_data(user1.id)
    user2_graph_data_all_time, user2_graph_data_recent = get_graph_data(user2.id)
    print(f"User 1 all time: {user1_graph_data_all_time}")
    print(f"User 1 recent: {user1_graph_data_recent}")
    print(f"User 2 all time: {user2_graph_data_all_time}")
    print(f"User 2 recent: {user2_graph_data_recent}")

    if not user1_graph_data_all_time or not user2_graph_data_all_time or not user1_graph_data_recent or not user2_graph_data_recent:
        return jsonify({"error": "Could not fetch graph data for one or both users"}), 500
    return render_template('comparison.html', 
                           user1_graph_data_all_time=user1_graph_data_all_time, 
                           user1_graph_data_recent=user1_graph_data_recent, 
                           user2_graph_data_all_time=user2_graph_data_all_time, 
                           user2_graph_data_recent=user2_graph_data_recent, 
                           user1_name=user1.display_name, 
                           user2_name=user2.display_name)


@app.route('/compare_users_redirect', methods=['POST'])
def compare_users_redirect():
    # Handle the form submission and redirect to the comparison using share tokens.
    user1_share_token = request.form['user1ShareToken']
    user2_share_token = request.form['user2ShareToken']
    return redirect(url_for('comparison', user1_share_token=user1_share_token, user2_share_token=user2_share_token))

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/input_playlist')
def input_playlist():
    return render_template('input_playlist.html')

def split_list_into_chunks(lst, chunk_size):
    """Yield successive chunk_size chunks from lst."""
    for i in range(0, len(lst), chunk_size):
        yield lst[i:i + chunk_size]

@app.route('/playlist_fetch', methods=['POST'])
def playlist_fetch(): #check to make sure it's not a Spotify playlist
    data = request.get_json()
    spotifyURL = data.get('playlistURL')
    
    if spotifyURL:
        parsed_url = urlparse(spotifyURL)
        path_parts = parsed_url.path.split('/')
        spotifyID = path_parts[-1] 
        playlist = sp.playlist(spotifyID)

        playlist_title = playlist.get('name')
        playlist_cover_photo = playlist['images'][0]['url'] if playlist.get('images') else None

        # Extract songs and artists
        songs = []
        artist_ids = set()
        for track in playlist['tracks']['items']:
            song = {
                'title': track['track']['name'], 
                'artist': track['track']['artists'][0]['name'], 
                'id': track['track']['id']
            }
            songs.append(song)
            # Add all artist IDs for each track to ensure uniqueness
            for artist in track['track']['artists']:
                artist_ids.add(artist['id'])

        artist_ids_list = list(artist_ids)  # Convert set to list for chunking
        artist_chunks = list(split_list_into_chunks(artist_ids_list, 50))  # Split into chunks of 50

        artists_info = []
        genres_pre = []
        for chunk in artist_chunks:
            artists_batch = sp.artists(chunk)
            genres_pre.append(get_artist_genres_batch(artists_batch))
            for artist in artists_batch['artists']:
                artists_info.append({
                    'name': artist['name'],
                    'id': artist['id'],
                    'genres': artist['genres'],
                    'popularity': artist['popularity'],
                    'image': artist['images'][0]['url'] if artist['images'] else None
                })
        
        genres_final = get_genre_count_batch(genres_pre)
        song_data = get_tracks_info_batch(playlist['tracks']['items'])
        audio_features = get_audio_features_tracks(song_data, sp)
        
        playlist_details = {
            'playlistTitle': playlist_title,
            'playlistCoverPhoto': playlist_cover_photo,
            'playlistURL': spotifyURL,
            'medianValues': audio_features,
            'songs': songs,
            'artists': artists_info,
            'genres': genres_final
        }
        
        return jsonify({'message': 'Playlist details fetched successfully', 'playlistDetails': playlist_details})
    else:
        return jsonify({'error': 'No playlist URL provided'}), 400
    
@app.route('/view_playlist')
def view_playlist():
    return render_template('view_playlist.html')

@app.route('/error')
def error_page():
    return render_template('error.html')

if __name__ == '__main__':
    app.run(debug=True, port=4000)
