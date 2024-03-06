from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

def generate_sharing_token():
    # TODO
    return 

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
    stats = db.relationship('UserStats', backref='user', lazy=True, cascade="all, delete")

    def __repr__(self):
        return f'<User {self.display_name}>'

class UserStats(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    genres_r = db.relationship('RecentGenres', backref='user_stats', lazy=True, cascade="all, delete")
    genres_a = db.relationship('AllTimeGenres', backref='user_stats', lazy=True, cascade="all, delete")
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
    user_stats_id = db.Column(db.Integer, db.ForeignKey('user_stats.id'), nullable=False)
    genre = db.Column(db.String(100))
    genre_count = db.Column(db.Integer)
    

class AllTimeGenres(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_stats_id = db.Column(db.Integer, db.ForeignKey('user_stats.id'), nullable=False)
    genre = db.Column(db.String(100))
    genre_count = db.Column(db.Integer)

class RecentArtists(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_stats_id = db.Column(db.Integer, db.ForeignKey('user_stats.id'), nullable=False)
    artist = db.Column(db.String(100))

class AllTimeArtists(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_stats_id = db.Column(db.Integer, db.ForeignKey('user_stats.id'), nullable=False)
    artist = db.Column(db.String(100))

def get_db_genres(user_id, time_range):
    # param user_id: user.id 
    # param time_range: 'r' for recent genres, 'a' for all time genres

    user_stats = UserStats.query.filter_by(user_id=user_id).first()

    if time_range == 'r':
        if user_stats:
            recent_genres = RecentGenres.query \
                            .filter_by(user_stats_id=user_stats.id) \
                            .order_by(RecentGenres.id.asc()) \
                            .all()
        
            genres_list = [genre.genre for genre in recent_genres]
            return genres_list
        else:
            return []
    elif time_range == 'a':
    
        if user_stats:
            all_time_genres = AllTimeGenres.query \
                            .filter_by(user_stats_id=user_stats.id) \
                            .order_by(AllTimeGenres.id.asc()) \
                            .all()
        
            genres_list = [genre.genre for genre in all_time_genres]
            return genres_list
        else:
            return []
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
    
def get_db_median_values(user_id, time_range):
    # param user_id: user.id
    # param time_range: 'r' for recent genres, 'a' for all time genres

    user_stats = UserStats.query.filter_by(user_id=user_id).first()

    if time_range == 'r':
        median_values = [user_stats.tempo_r, user_stats.loudness_r, user_stats.acousticness_r, user_stats.danceability_r, user_stats.valence_r, user_stats.energy_r, user_stats.speechiness_r, user_stats.popularity_r, user_stats.variance_r]
        return median_values
    elif time_range == 'a':
        median_values = [user_stats.tempo_a, user_stats.loudness_a, user_stats.acousticness_a, user_stats.danceability_a, user_stats.valence_a, user_stats.energy_a, user_stats.speechiness_a, user_stats.popularity_a, user_stats.variance_a]
        return median_values
    else:
        # error handling
        raise ValueError("Incorrect time_range input. Expected 'r' for recent or 'a' for all time genres.")

