from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import string, random

db = SQLAlchemy()

def generate_sharing_token():
    possible_characters = string.ascii_letters + string.digits
    share_token = ""
    for i in range(0,5):
        random_character = random.choice(possible_characters)
        share_token += random_character
    
    return share_token

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    spotify_id = db.Column(db.String(128), unique=True, nullable=False)
    display_name = db.Column(db.String(128), nullable=False)
    profile_pic = db.Column(db.String(256))
    access_token = db.Column(db.String(256), nullable=False)
    refresh_token = db.Column(db.String(256), nullable=False)
    token_expires_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    most_recent_login = db.Column(db.DateTime, default=datetime.utcnow)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    share_token = db.Column(db.String(5), nullable=False)
    stats = db.relationship('UserStats', backref='user', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f'<User {self.display_name}>'

class UserStats(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    genres_r = db.relationship('RecentGenres', backref='user_stats', lazy=True, cascade="all, delete-orphan")
    genres_a = db.relationship('AllTimeGenres', backref='user_stats', lazy=True, cascade="all, delete-orphan")
    artists_r = db.relationship('RecentArtists', backref='user_stats', lazy=True, cascade="all, delete-orphan")
    artists_a = db.relationship('AllTimeArtists', backref='user_stats', lazy=True, cascade="all, delete-orphan")
    tracks_r = db.relationship('RecentTracks', backref='user_stats', lazy=True, cascade="all, delete-orphan")
    tracks_a = db.relationship('AllTimeTracks', backref='user_stats', lazy=True, cascade="all, delete-orphan")
    popularity_r = db.Column(db.Float)
    popularity_a = db.Column(db.Float)
    tempo_r = db.Column(db.Float)
    tempo_a = db.Column(db.Float)
    loudness_r = db.Column(db.Float)
    loudness_a = db.Column(db.Float)
    acousticness_r = db.Column(db.Float)
    acousticness_a = db.Column(db.Float)
    danceability_r = db.Column(db.Float)
    danceability_a = db.Column(db.Float)
    valence_r = db.Column(db.Float)
    valence_a = db.Column(db.Float)
    energy_r = db.Column(db.Float)
    energy_a = db.Column(db.Float)
    speechiness_r = db.Column(db.Float)
    speechiness_a = db.Column(db.Float)
    variance_r = db.Column(db.Float)
    variance_a = db.Column(db.Float)


class RecentGenres(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_stats_id = db.Column(db.Integer, db.ForeignKey('user_stats.id', ondelete='CASCADE'), nullable=False)
    genre = db.Column(db.String(100))
    genre_count = db.Column(db.Integer)
    

class AllTimeGenres(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_stats_id = db.Column(db.Integer, db.ForeignKey('user_stats.id', ondelete='CASCADE'), nullable=False)
    genre = db.Column(db.String(100))
    genre_count = db.Column(db.Integer)

class RecentArtists(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_stats_id = db.Column(db.Integer, db.ForeignKey('user_stats.id', ondelete='CASCADE'), nullable=False)
    artist = db.Column(db.String(100))

class AllTimeArtists(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_stats_id = db.Column(db.Integer, db.ForeignKey('user_stats.id', ondelete='CASCADE'), nullable=False)
    artist = db.Column(db.String(100))

class RecentTracks(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_stats_id = db.Column(db.Integer, db.ForeignKey('user_stats.id', ondelete='CASCADE'), nullable=False)
    song = db.Column(db.String(100))

class AllTimeTracks(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_stats_id = db.Column(db.Integer, db.ForeignKey('user_stats.id', ondelete='CASCADE'), nullable=False)
    song = db.Column(db.String(100))

def load_user_stats(user_id, median_values_r, median_values_a, new_data, update):
    if update:
        user_stats = UserStats.query.filter_by(user_id=user_id).first()

        if not user_stats:
            raise ValueError("UserStats not found")
        
        db.session.delete(user_stats)
        db.session.commit()

    user_stats = UserStats(
                user_id=user_id,
                popularity_r=median_values_r[7],
                popularity_a=median_values_a[7],
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
                variance_r=median_values_r[8],
                variance_a=median_values_r[8]
            )
    db.session.add(user_stats)
    db.session.commit()

    for g, count in new_data["recent_genres"].items():
        new_genre = RecentGenres(
            user_stats_id=user_stats.id,
            genre=g,
            genre_count=count
        )
        db.session.add(new_genre)
    
    for g, count in new_data["all_time_genres"].items():
        new_genre = AllTimeGenres(
            user_stats_id=user_stats.id,
            genre=g,
            genre_count=count
        )
        db. session.add(new_genre)

    for a in new_data["recent_artists"]:
        new_artist = RecentArtists(
            user_stats_id=user_stats.id,
            artist=a
        )
        db.session.add(new_artist)

    for a in new_data["all_time_artists"]:
        new_artist = AllTimeArtists(
            user_stats_id=user_stats.id,
            artist=a
        )
        db. session.add(new_artist)

    for track in new_data["recent_tracks"]:
        new_track = RecentTracks(
            user_stats_id=user_stats.id,
            song=track
        )
        db.session.add(new_track)

    for track in new_data["all_time_tracks"]:
        new_track = AllTimeTracks(
            user_stats_id=user_stats.id,
            song=track
        )
        db. session.add(new_track)

    db.session.commit()


def get_db_genres(user_id, time_range):
    # param user_id: user.id 
    # param time_range: 'r' for recent genres, 'a' for all time genres

    user_stats = UserStats.query.filter_by(user_id=user_id).first()

    genre_dict = {}

    if time_range == 'r':
        if user_stats:
            recent_genres = RecentGenres.query \
                            .filter_by(user_stats_id=user_stats.id) \
                            .order_by(RecentGenres.id.asc()) \
                            .all()
        
            # set genres_dict to (key, value) --> (genre, count)
            for genre in recent_genres:
                genre_dict[genre.genre] = genre.genre_count
            
            return genre_dict
        else:
            return {}
    elif time_range == 'a':
    
        if user_stats:
            all_time_genres = AllTimeGenres.query \
                            .filter_by(user_stats_id=user_stats.id) \
                            .order_by(AllTimeGenres.id.asc()) \
                            .all()
        
            for genre in all_time_genres:
                genre_dict[genre.genre] = genre.genre_count
            return genre_dict
        else:
            return {}
    else:
        # error handling
        raise ValueError("Incorrect time_range input. Expected 'r' for recent or 'a' for all time genres.")

def get_db_artists(user_id, time_range):
    # param user_id: user.id 
    # param time_range: 'r' for recent genres, 'a' for all time genres

    user_stats = UserStats.query.filter_by(user_id=user_id).first()

    if time_range == 'r':
        if user_stats:
            recent_artists = RecentArtists.query \
                            .filter_by(user_stats_id=user_stats.id) \
                            .order_by(RecentArtists.id.asc()) \
                            .all()
        
            artist_list = [artist.artist for artist in recent_artists]
            return artist_list
        else:
            return []
    elif time_range == 'a':
    
        if user_stats:
            all_time_artists = AllTimeArtists.query \
                            .filter_by(user_stats_id=user_stats.id) \
                            .order_by(AllTimeArtists.id.asc()) \
                            .all()
        
            artist_list = [artist.artist for artist in all_time_artists]
            return artist_list
        else:
            return []
    else:
        # error handling
        raise ValueError("Incorrect time_range input. Expected 'r' for recent or 'a' for all time genres.")
    
def get_db_tracks(user_id, time_range):
    # param user_id: user.id 
    # param time_range: 'r' for recent genres, 'a' for all time genres

    user_stats = UserStats.query.filter_by(user_id=user_id).first()

    if time_range == 'r':
        if user_stats:
            recent_tracks = RecentTracks.query \
                            .filter_by(user_stats_id=user_stats.id) \
                            .order_by(RecentTracks.id.asc()) \
                            .all()
        
            track_list = [track.song for track in recent_tracks]
            return track_list
        else:
            return []
    elif time_range == 'a':
    
        if user_stats:
            all_time_tracks = AllTimeTracks.query \
                            .filter_by(user_stats_id=user_stats.id) \
                            .order_by(AllTimeTracks.id.asc()) \
                            .all()
        
            track_list = [track.song for track in all_time_tracks]
            return track_list
        else:
            return []
    else:
        # error handling
        raise ValueError("Incorrect time_range input. Expected 'r' for recent or 'a' for all time genres.")
    
def get_db_median_values(user_id, time_range):
    # param user_id: user.id
    # param time_range: 'r' for recent genres, 'a' for all time genres

    user_stats = UserStats.query.filter_by(user_id=user_id).first()
    median_values = {}
    if time_range == 'r':
        median_values["tempo"] = user_stats.tempo_r
        median_values["loudness"] = user_stats.loudness_r
        median_values["acousticness"] = user_stats.acousticness_r
        median_values["danceability"] = user_stats.danceability_r
        median_values["valence"] = user_stats.valence_r
        median_values["energy"] = user_stats.energy_r
        median_values["speechiness"] = user_stats.speechiness_r
        median_values["popularity"] = user_stats.popularity_r
        median_values["variance"] = user_stats.variance_r

        return median_values
    elif time_range == 'a':
        median_values["tempo"] = user_stats.tempo_a
        median_values["loudness"] = user_stats.loudness_a
        median_values["acousticness"] = user_stats.acousticness_a
        median_values["danceability"] = user_stats.danceability_a
        median_values["valence"] = user_stats.valence_a
        median_values["energy"] = user_stats.energy_a
        median_values["speechiness"] = user_stats.speechiness_a
        median_values["popularity"] = user_stats.popularity_a
        median_values["variance"] = user_stats.variance_a
        
        return median_values
    else:
        # error handling
        raise ValueError("Incorrect time_range input. Expected 'r' for recent or 'a' for all time genres.")

