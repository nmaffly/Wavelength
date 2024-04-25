from flask import Flask, render_template, redirect, request, session, jsonify, url_for
import spotipy
import os
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
from extraction import get_tracks_info, get_tracks_info_batch, get_artists_info, get_artist_genres_batch, get_artist_genres_batch, get_genre_count, get_genre_count_batch, get_popularity, get_audio_features_tracks, get_variance
from datetime import datetime, timedelta
from flask_migrate import Migrate
from flask_session import Session
from database import User, UserStats, Matches, db
from db_functions import get_db_genres, get_db_artists, get_db_median_values, get_db_tracks, generate_random_sharing_token, generate_four_letter_sharing_token, load_user_stats, taken_tokens
from urllib.parse import urlparse

load_dotenv()

# FOR TESTNG
update_db = True
          # True --> immediate spotify extraction and DB update
          # False --> pull stats from DB

app = Flask(__name__)

# Configure the Flask app to use Flask-Session
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY')

import os

app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{os.getenv("MYSQL_USER")}:{os.getenv("MYSQL_PASSWORD")}@{os.getenv("MYSQL_HOST")}/{os.getenv("MYSQL_DB")}'


db.init_app(app)
migrate = Migrate(app, db)

def setup_spotify(team):
    print(f"Setting up Spotify for team {team}")
    SPOTIPY_CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
    SPOTIPY_CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET')
    SPOTIPY_REDIRECT_URI = os.getenv('SPOTIPY_REDIRECT_URI')



    # Initialize Spotify auth with team-specific details
    auth_manager = SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET, redirect_uri=SPOTIPY_REDIRECT_URI,
                                scope='user-library-read user-top-read user-read-currently-playing')
    sp = spotipy.Spotify(auth_manager=auth_manager)
    return sp, auth_manager

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        team_option = request.form['options'] ## We can use this value to switch between the OAuth
        print('Selected team option:', team_option)
        session['team_option'] = team_option
    cleanup()
    sp, auth_manager = setup_spotify(team_option)
    auth_url = auth_manager.get_authorize_url() 
    return redirect(auth_url)

@app.route('/callback')
def callback():
    code = request.args.get('code')
    cleanup()
    sp, auth_manager = setup_spotify(session.get('team_option', 1))
    token_info = auth_manager.get_access_token(code)
    session['token_info'] = token_info

    if not token_info:
        return redirect('/login')
    if auth_manager.is_token_expired(token_info):
        token_info = auth_manager.refresh_access_token(token_info['refresh_token'])
        session['token_info'] = token_info

    spotify = spotipy.Spotify(auth=token_info['access_token'])
    user_data = spotify.current_user()
    user = User.query.filter_by(spotify_id=user_data['id']).first()
    new_user = True
    if user:
        new_user = False
        return render_template('loading.html', new_user = new_user)
    else:
        return render_template('new_profile.html')


@app.route('/fetch_data')
def fetch_data():
    team = session.get('team_option', 1)

    sp, sp_oauth = setup_spotify(team)
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

    # Will get set to false if it's a new user
    get_matches = True

    if user and not user.last_updated:
        user.last_updated = user.created_at
    
    if(update_db):
        update_time_range = timedelta(seconds=1)
    else:
        update_time_range = timedelta(weeks=1)

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
            "user_data": user_data,
            "user_name": user.display_name,
            "profile_pic": user.profile_pic,
            "share_token": user.share_token,
        }

    else:
        # otherwise extract spotify info, add to database and session
        print("User doesn't exist, or it's been longer than 30 seconds, new data being pulled")
        # stored user data
        user_name = user_data['display_name']
        profile_pic = "../static/icons/no_user.png"
        if 'images' in user_data and len(user_data['images']) > 1:
            # Check if 'url' key exists in the second image and it is not None or empty
            if 'url' in user_data['images'][1] and user_data['images'][1]['url']:
                profile_pic = user_data['images'][1]['url']
                print("First: ", profile_pic)

        if profile_pic == None:
            profile_pic = "../static/icons/no_user.png"
        print("Second: ",profile_pic)

        # extracted recent data 
        top_artists_r = spotify.current_user_top_artists(limit=50, time_range='short_term')['items']
        top_tracks_r = spotify.current_user_top_tracks(limit=50, time_range='short_term')['items']

        # extracted all time data
        top_artists_m = spotify.current_user_top_artists(limit=50, time_range='medium_term')['items']
        top_tracks_m = spotify.current_user_top_tracks(limit=50, time_range='medium_term')['items']
        
        # extracted all time data
        top_artists_a = spotify.current_user_top_artists(limit=50, time_range='long_term')['items']
        top_tracks_a = spotify.current_user_top_tracks(limit=50, time_range='long_term')['items']

        # Recent (1 month) stats
        artists_info_r = get_artists_info(top_artists_r) # dictionary with top artists and associated info
        genres_r = get_genre_count(artists_info_r)
        tracks_r = get_tracks_info(top_tracks_r)
        popularity_r = get_popularity(top_artists_r)
        median_values_r = get_audio_features_tracks(tracks_r, spotify)
        variance_r = get_variance() 
        median_values_r['popularity'] = popularity_r
        median_values_r['variance'] = variance_r

        # Medium term (6 months) stats
        artists_info_m = get_artists_info(top_artists_m) # dictionary with top artists and associated info
        genres_m = get_genre_count(artists_info_m)
        tracks_m = get_tracks_info(top_tracks_m)
        popularity_m = get_popularity(top_artists_m)
        median_values_m = get_audio_features_tracks(tracks_m, spotify)
        variance_m = get_variance()
        median_values_m['popularity'] = popularity_m
        median_values_m['variance'] = variance_m

        # All Time stats
        artists_info_a = get_artists_info(top_artists_a) # dictionary with top artists and associated info
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
            get_matches = False
            #if the user doesn't exist, create new user
            # setting up db entry for new user
            user_share_token = generate_four_letter_sharing_token()
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
            try:
                db.session.add(user)
                db.session.commit()
            except Exception as e:
                # Handle database errors, such as connection issues or constraints violations
                print(f"Unable to commit to session: {e}")
                db.session.rollback()
                print('db session rolled back')
                return jsonify(error=str(e)), 500
            
            print("user instanced added to db session")
            
            load_user_stats(user.id, median_values_r,median_values_m, median_values_a, new_data, update=False)
        else:
            # the user exists, update info in db
            user.last_updated = datetime.utcnow()
            user.most_recent_login = datetime.utcnow()
            load_user_stats(user.id, median_values_r, median_values_m, median_values_a, new_data, update=True)
            
        session['processed_data'] = {
            "user_data": user_data,
            "user_name": user_name,
            "profile_pic": profile_pic,
            "share_token": user.share_token,
        }

    try:
        db.session.commit()
        print("successfully commited to session")
    except Exception as e:
        # Handle database errors, such as connection issues or constraints violations
        print(f"Unable to commit to session: {e}")
        db.session.rollback()
        return jsonify(error=str(e)), 500

    return jsonify(success=True)

def cleanup():
    cache_file = '.cache'
    if os.path.exists(cache_file):
        os.remove(cache_file)

@app.route('/display')
def display():
    # Get user's matches
    processed_data = session.get('processed_data', {})
    if not processed_data:
        return redirect('/')
    user1 = User.query.filter_by(spotify_id=session['processed_data']['user_data']['id']).first()
    if user1.first_name == None:
        return redirect('/new_profile')
    user_name = session['processed_data']['user_name']
    share_code = session['processed_data']['share_token']
    median_values_r = get_db_median_values(user1.id, 'r')
    median_values_m = get_db_median_values(user1.id, 'm')
    median_values_a = get_db_median_values(user1.id, 'a')

    processed_data = {
            "graph_json": {
                "median_values_r": median_values_r, 
                "median_values_m": median_values_m, 
                "median_values_a": median_values_a
            },
            "median_values_r": median_values_r,
            "median_values_m": median_values_m, 
            "median_values_a": median_values_a,
            "user_data": session['processed_data']['user_data'],
            "user_name": session['processed_data']['user_name'],
            "profile_pic": session['processed_data']['profile_pic'],
            "share_token": session['processed_data']['share_token'],
            "genre_r": get_db_genres(user1.id, 'r'),
            "genre_m": get_db_genres(user1.id, 'm'),
            "genre_a": get_db_genres(user1.id, 'a'),
            "artists_a": get_db_artists(user1.id, 'a'),
            "artists_m": get_db_artists(user1.id, 'm'),
            "artists_r": get_db_artists(user1.id, 'r'),
            "tracks_r": get_db_tracks(user1.id,'r'),
            "tracks_m": get_db_tracks(user1.id, 'm'),
            "tracks_a": get_db_tracks(user1.id,'a'),
        }

    matches_data = []
    matches = Matches.query.filter((Matches.user1_id == user1.id) | (Matches.user2_id == user1.id)).all()
    for match in matches:
        other_user_id = match.user1_id if match.user1_id != user1.id else match.user2_id
        other_user = User.query.get(other_user_id)
        match_data = {
            "name": f"{other_user.first_name} {other_user.last_name}",
            "profile_pic": other_user.profile_pic,
            "home_town": other_user.hometown,
            "age": other_user.age,
            "match_percentage": match.compatibility,
            "share_token": other_user.share_token
        }
        matches_data.append(match_data)

    taken_tokens_list = taken_tokens() or []
    print(taken_tokens_list)

    return render_template('user_dashboard.html', user_name = user_name, share_token = share_code, taken_tokens=taken_tokens_list, processed_data=processed_data, matches_data=matches_data)

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
        'speechiness': user_stats.speechiness_a,
        'popularity': user_stats.popularity_a,
        'tempo': user_stats.tempo_a,
        'valence': user_stats.valence_a
    }
    graph_data_recent = {
        'acousticness': user_stats.acousticness_r,
        'danceability': user_stats.danceability_r,
        'energy': user_stats.energy_r,
        'speechiness': user_stats.speechiness_r,
        'popularity': user_stats.popularity_r,
        'tempo': user_stats.tempo_r,
        'valence': user_stats.valence_r
    }
    graph_data_medium = {
        'acousticness': user_stats.acousticness_m,
        'danceability': user_stats.danceability_m,
        'energy': user_stats.energy_m,
        'speechiness': user_stats.speechiness_m,
        'popularity': user_stats.popularity_m,
        'tempo': user_stats.tempo_m,
        'valence': user_stats.valence_m
    }
    return graph_data_all_time, graph_data_recent, graph_data_medium

@app.route('/comparison', methods=['GET', 'POST']) #need this to grab top artists and potentially shared songs
def comparison():
    if request.method == 'POST':
        user_share_token = request.form.get('user_share_token')  
    elif request.method == 'GET':
        user_share_token = request.args.get('token')
        already_matched = True
    
    user1_share_token = session['processed_data']['share_token']

    user1 = User.query.filter_by(share_token=user1_share_token).first()
    print(vars(user1))
    user2 = User.query.filter_by(share_token=user_share_token).first()
    
    user1_graph_data_all_time, user1_graph_data_recent, user1_graph_data_medium = get_graph_data(user1.id)
    user2_graph_data_all_time, user2_graph_data_recent, user2_graph_data_medium = get_graph_data(user2.id)

    shared_genres_r, shared_genres_m, shared_genres_a = get_shared_genres(user1.id, user2.id)
    shared_artists_r, shared_artists_m, shared_artists_a = get_shared_artists(user1.id, user2.id)

    # user1_avg_values = get_avg_values(user1_graph_data_all_time, user1_graph_data_recent, user1_graph_data_medium)
    # user2_avg_values = get_avg_values(user2_graph_data_all_time, user2_graph_data_recent, user2_graph_data_medium)

    if not user1_graph_data_all_time or not user2_graph_data_all_time or not user1_graph_data_recent or not user2_graph_data_recent:
        return jsonify({"error": "Could not fetch graph data for one or both users"}), 500
    
    match = Matches.query.filter(
        (Matches.user1_id == user1.id) & (Matches.user2_id == user2.id) | 
        (Matches.user1_id == user2.id) & (Matches.user2_id == user1.id)
    ).first()

    compatibility_score_recent = calculate_compatibility(user1.id, user2.id, user1_graph_data_recent, user2_graph_data_recent)
    compatibility_score_medium = calculate_compatibility(user1.id, user2.id, user1_graph_data_medium, user2_graph_data_medium)
    compatibility_score_allTime = calculate_compatibility(user1.id, user2.id, user1_graph_data_all_time, user2_graph_data_all_time)

    if match:
        match.compatibility = compatibility_score_recent
    else:
        match = Matches(
            user1_id=user1.id, 
            user2_id=user2.id, 
            compatibility=compatibility_score_recent
        )
    print(user1.first_name)
    db.session.add(match)
    db.session.commit()

    return render_template('comparison.html', 
                    user1_graph_data_all_time=user1_graph_data_all_time, 
                    user1_graph_data_recent=user1_graph_data_recent, 
                    user1_graph_data_medium=user1_graph_data_medium, 
                    user2_graph_data_all_time=user2_graph_data_all_time, 
                    user2_graph_data_recent=user2_graph_data_recent, 
                    user2_graph_data_medium=user2_graph_data_medium, 
                    user1_name=user1.first_name, 
                    user2_name=user2.first_name,
                    compatibility_score_recent=int(round(compatibility_score_recent, 0)),
                    compatibility_score_medium=int(round(compatibility_score_medium, 0)),
                    compatibility_score_all_time=int(round(compatibility_score_allTime, 0)),
                    shared_genres_r=shared_genres_r[:10], 
                    shared_genres_m=shared_genres_m[:10], 
                    shared_genres_a=shared_genres_a[:10], 
                    shared_artists_r=shared_artists_r[:10], 
                    shared_artists_m=shared_artists_m[:10], 
                    shared_artists_a=shared_artists_a[:10]
                )

def get_shared_genres(user1_id, user2_id):
    user1_genres_r = set(get_db_genres(user1_id, 'r'))
    user2_genres_r = set(get_db_genres(user2_id, 'r'))

    user1_genres_m = set(get_db_genres(user1_id, 'm'))
    user2_genres_m = set(get_db_genres(user2_id, 'm'))

    user1_genres_a = set(get_db_genres(user1_id, 'a'))
    user2_genres_a = set(get_db_genres(user2_id, 'a'))

    common_genres_r = list(user1_genres_r.intersection(user2_genres_r))
    common_genres_m = list(user1_genres_m.intersection(user2_genres_m))
    common_genres_a = list(user1_genres_a.intersection(user2_genres_a))

    return common_genres_r, common_genres_m, common_genres_a

def get_shared_artists(user1_id, user2_id):
    user1_artists_r = set([artist['name'] for artist in get_db_artists(user1_id, 'r')])
    print(user1_artists_r)
    user2_artists_r = set([artist['name'] for artist in get_db_artists(user2_id, 'r')])

    user1_artists_m = set([artist['name'] for artist in get_db_artists(user1_id, 'm')])
    user2_artists_m = set([artist['name'] for artist in get_db_artists(user2_id, 'm')])

    user1_artists_a = set([artist['name'] for artist in get_db_artists(user1_id, 'a')])
    user2_artists_a = set([artist['name'] for artist in get_db_artists(user2_id, 'a')])

    common_artists_r = list(user1_artists_r.intersection(user2_artists_r))
    common_artists_m = list(user1_artists_m.intersection(user2_artists_m))
    common_artists_a = list(user1_artists_a.intersection(user2_artists_a))
    print(common_artists_a)

    return common_artists_r, common_artists_m, common_artists_a


def get_avg_values(all_time, recent, medium):
    avg_values = []
    avg_values.append((all_time['acousticness'] + recent['acousticness'] + medium['acousticness']) / 3)
    avg_values.append((all_time['danceability'] + recent['danceability'] + medium['danceability']) / 3)
    avg_values.append((all_time['energy'] + recent['energy'] + medium['energy']) / 3)
    avg_values.append((all_time['speechiness'] + recent['speechiness'] + medium['speechiness']) / 3)
    avg_values.append((all_time['popularity'] + recent['popularity'] + medium['popularity']) / 3)
    avg_values.append((all_time['tempo'] + recent['tempo'] + medium['tempo']) / 3)
    avg_values.append((all_time['valence'] + recent['valence'] + medium['valence']) / 3)

    return avg_values

def calculate_compatibility(user1_id, user2_id, user1_values, user2_values):
    score = 0

    user1_vals_list = [user1_values['acousticness'], user1_values['danceability'], user1_values['energy'], user1_values['speechiness'], user1_values['popularity'], user1_values['tempo'], user1_values['valence']]
    user2_vals_list = [user2_values['acousticness'], user2_values['danceability'], user2_values['energy'], user2_values['speechiness'], user2_values['popularity'], user2_values['tempo'], user2_values['valence']]

    for x in range(0, len(user1_vals_list)):
        larger_val = max(user1_vals_list[x], user2_vals_list[x])
        smaller_val = min(user1_vals_list[x], user2_vals_list[x])
        percent_diff = (larger_val - smaller_val) / (larger_val+0.01)
        print(f'percent diff: {percent_diff}')
        score_multiplier = 1 - percent_diff
        score += (14.2857 * score_multiplier)

    return score

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
            genres_pre.append(get_artist_genres_batch(artists_batch)) #need to create a function to count the artists' appearance in the playlist
                                                                    # and then sort by that method
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
        # Add playlist details to database, preferably by each variable in the dict
        return jsonify({'message': 'Playlist details fetched successfully', 'playlistDetails': playlist_details})
    else:
        return jsonify({'error': 'No playlist URL provided'}), 400
    
@app.route('/view_playlist')
def view_playlist():
    return render_template('view_playlist.html')

@app.route('/new_profile')
def new_profile():
    print('new_profile route reached')
    return render_template('new_profile.html')

@app.route('/submit_new_profile', methods=['POST'])
def submit_new_profile():
    if request.method == 'POST':
        print('Submission of new profile route reached')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        age = request.form.get('age')
        hometown = request.form.get('hometown')
        print("First Name:", first_name)  # This will help verify what is being received
        
        # Assuming the user data is stored in the session correctly
        user_data = session.get('processed_data', {}).get('user_data')
        if not user_data or 'id' not in user_data:
            raise Exception("No user data available or user data is incomplete.")

        user = User.query.filter_by(spotify_id=user_data['id']).first()
        if not user:
            raise Exception("No user found with the given Spotify ID.")

        user.first_name = first_name
        user.last_name = last_name
        user.age = age
        user.hometown = hometown

        db.session.commit()

    return redirect(url_for('display'))


@app.route('/delete_user', methods=['POST'])
def delete_user():
    if 'user_data' not in session['processed_data']:
        return jsonify({'error': 'User not logged in'}), 401 

    user_data = session['processed_data']['user_data']
    user = User.query.filter_by(spotify_id=user_data['id']).first()

    if not user:
        return jsonify({'error': 'User not found'}), 404 

    try:
        Matches.query.filter((Matches.user1_id == user.id) | (Matches.user2_id == user.id)).delete()
        db.session.delete(user)  # Delete the user from the database
        db.session.commit()
        session.clear() # clear session data
        return redirect(url_for('index'))
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500 
    
@app.errorhandler(404)
def page_not_found(e):
    # you can log the error here if you want
    print("A 404 error occurred:", str(e))
    # Redirect to the error page with error information
    return render_template('error.html', error_message=e), 404

@app.errorhandler(500)
def wrong_team(e):
    # you can log the error here if you want
    print("A 404 error occurred:", str(e))
    # Redirect to the error page with error information
    return render_template('wrong_team.html', error_message=e), 500

# @app.errorhandler(Exception)
# def handle_exception(e):
#     return render_template('error.html', error_message=e), 500

@app.route('/test-error')
def test_error():
    raise Exception("This is a test error")

@app.route('/test_error_page')
def test_error_page():
    # Directly testing error page redirection
    return redirect(url_for('error_page', error_message="Test error message"))

@app.route('/error_page')
def error_page():
    print('Error page reached')
    error_message = request.args.get('error_message', default='An unexpected error occurred.')
    return render_template('error.html', error_message=error_message)


if __name__ == '__main__':
    app.run(debug=True, port=4000)
