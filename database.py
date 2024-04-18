from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import string, random

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    spotify_id = db.Column(db.String(128), unique=True, nullable=False)
    display_name = db.Column(db.String(128), nullable=False)
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    age = db.Column(db.Integer)
    hometown = db.Column(db.String(64))
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
    
class Matches(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user1_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    user2_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    compatibility = db.Column(db.Float)

    user1 = db.relationship('User', foreign_keys=[user1_id], backref=db.backref('matches_as_user1', lazy=True))
    user2 = db.relationship('User', foreign_keys=[user2_id], backref=db.backref('matches_as_user2', lazy=True))



class UserStats(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    genres_r = db.relationship('RecentGenres', backref='user_stats', lazy=True, cascade="all, delete-orphan")
    genres_m = db.relationship('MediumGenres', backref='user_stats', lazy=True, cascade="all, delete-orphan")
    genres_a = db.relationship('AllTimeGenres', backref='user_stats', lazy=True, cascade="all, delete-orphan")
    artists_r = db.relationship('RecentArtists', backref='user_stats', lazy=True, cascade="all, delete-orphan")
    artists_m = db.relationship('MediumArtists', backref='user_stats', lazy=True, cascade="all, delete-orphan")
    artists_a = db.relationship('AllTimeArtists', backref='user_stats', lazy=True, cascade="all, delete-orphan")
    tracks_r = db.relationship('RecentTracks', backref='user_stats', lazy=True, cascade="all, delete-orphan")
    tracks_m = db.relationship('MediumTracks', backref='user_stats', lazy=True, cascade="all, delete-orphan")
    tracks_a = db.relationship('AllTimeTracks', backref='user_stats', lazy=True, cascade="all, delete-orphan")
    popularity_r = db.Column(db.Float)
    popularity_m = db.Column(db.Float)
    popularity_a = db.Column(db.Float)
    tempo_r = db.Column(db.Float)
    tempo_m = db.Column(db.Float)
    tempo_a = db.Column(db.Float)
    loudness_r = db.Column(db.Float)
    loudness_m = db.Column(db.Float)
    loudness_a = db.Column(db.Float)
    acousticness_r = db.Column(db.Float)
    acousticness_m = db.Column(db.Float)
    acousticness_a = db.Column(db.Float)
    danceability_r = db.Column(db.Float)
    danceability_m = db.Column(db.Float)
    danceability_a = db.Column(db.Float)
    valence_r = db.Column(db.Float)
    valence_m = db.Column(db.Float)
    valence_a = db.Column(db.Float)
    energy_r = db.Column(db.Float)
    energy_m = db.Column(db.Float)
    energy_a = db.Column(db.Float)
    speechiness_r = db.Column(db.Float)
    speechiness_m = db.Column(db.Float)
    speechiness_a = db.Column(db.Float)
    variance_r = db.Column(db.Float)
    variance_m = db.Column(db.Float)
    variance_a = db.Column(db.Float)

class RecentGenres(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_stats_id = db.Column(db.Integer, db.ForeignKey('user_stats.id', ondelete='CASCADE'), nullable=False)
    genre = db.Column(db.String(256))
    genre_count = db.Column(db.Integer)

class MediumGenres(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_stats_id = db.Column(db.Integer, db.ForeignKey('user_stats.id', ondelete='CASCADE'), nullable=False)
    genre = db.Column(db.String(256))
    genre_count = db.Column(db.Integer)
    

class AllTimeGenres(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_stats_id = db.Column(db.Integer, db.ForeignKey('user_stats.id', ondelete='CASCADE'), nullable=False)
    genre = db.Column(db.String(256))
    genre_count = db.Column(db.Integer)

class RecentArtists(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_stats_id = db.Column(db.Integer, db.ForeignKey('user_stats.id', ondelete='CASCADE'), nullable=False)
    artist = db.Column(db.String(256))
    img_url = db.Column(db.String(256))
    spotify_url = db.Column(db.String(256))
    href = db.Column(db.String(256))

class MediumArtists(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_stats_id = db.Column(db.Integer, db.ForeignKey('user_stats.id', ondelete='CASCADE'), nullable=False)
    artist = db.Column(db.String(256))
    img_url = db.Column(db.String(256))
    spotify_url = db.Column(db.String(256))
    href = db.Column(db.String(256))

class AllTimeArtists(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_stats_id = db.Column(db.Integer, db.ForeignKey('user_stats.id', ondelete='CASCADE'), nullable=False)
    artist = db.Column(db.String(256))
    img_url = db.Column(db.String(256))
    spotify_url = db.Column(db.String(256))
    href = db.Column(db.String(256))

class RecentTracks(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_stats_id = db.Column(db.Integer, db.ForeignKey('user_stats.id', ondelete='CASCADE'), nullable=False)
    song = db.Column(db.String(256))
    artist = db.Column(db.String(256))
    track_id = db.Column(db.String(256))
    album_art_img_url = db.Column(db.String(256))
    preview_url = db.Column(db.String(200))
    spotify_url = db.Column(db.String(256))
    href = db.Column(db.String(256))


class MediumTracks(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_stats_id = db.Column(db.Integer, db.ForeignKey('user_stats.id', ondelete='CASCADE'), nullable=False)
    song = db.Column(db.String(256))
    artist = db.Column(db.String(256))
    track_id = db.Column(db.String(256))
    album_art_img_url = db.Column(db.String(256))
    preview_url = db.Column(db.String(200))
    spotify_url = db.Column(db.String(256))
    href = db.Column(db.String(256))

class AllTimeTracks(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_stats_id = db.Column(db.Integer, db.ForeignKey('user_stats.id', ondelete='CASCADE'), nullable=False)
    song = db.Column(db.String(256))
    artist = db.Column(db.String(10000))
    track_id = db.Column(db.String(256))
    album_art_img_url = db.Column(db.String(256))
    preview_url = db.Column(db.String(200))
    spotify_url = db.Column(db.String(256))
    href = db.Column(db.String(256))

