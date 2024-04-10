from database import UserStats, RecentGenres, MediumGenres, AllTimeGenres, RecentArtists, MediumArtists, AllTimeArtists, RecentTracks, MediumTracks, AllTimeTracks, db
import string, random

def generate_sharing_token():
    possible_characters = string.ascii_letters + string.digits
    share_token = ""
    for i in range(0,5):
        random_character = random.choice(possible_characters)
        share_token += random_character
    
    return share_token

def load_user_stats(user_id, median_values_r, median_values_m, median_values_a, new_data, update):
    if update:
        user_stats = UserStats.query.filter_by(user_id=user_id).first()

        if not user_stats:
            raise ValueError("UserStats not found")
        
        db.session.delete(user_stats)
        db.session.commit()

    user_stats = UserStats(
        user_id=user_id,
        popularity_r=median_values_r['popularity'],
        popularity_m=median_values_m['popularity'], 
        popularity_a=median_values_a['popularity'],
        tempo_r=median_values_r['tempo'],
        tempo_m=median_values_m['tempo'],
        tempo_a=median_values_a['tempo'],
        loudness_r=median_values_r['loudness'],
        loudness_m=median_values_m['loudness'],
        loudness_a=median_values_a['loudness'],
        acousticness_r=median_values_r['acousticness'],
        acousticness_m=median_values_m['acousticness'],
        acousticness_a=median_values_a['acousticness'],
        danceability_r=median_values_r['danceability'],
        danceability_m=median_values_m['danceability'],
        danceability_a=median_values_a['danceability'],
        valence_r=median_values_r['valence'],
        valence_m=median_values_m['valence'],
        valence_a=median_values_a['valence'],
        energy_r=median_values_r['energy'],
        energy_m=median_values_m['energy'],
        energy_a=median_values_a['energy'],
        speechiness_r=median_values_r['speechiness'],
        speechiness_m=median_values_m['speechiness'],
        speechiness_a=median_values_a['speechiness'],
        variance_r=median_values_r['variance'],
        variance_m=median_values_m['variance'], 
        variance_a=median_values_a['variance']
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
    
    for g, count in new_data["medium_genres"].items():
        new_genre = MediumGenres(
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

    for artist_name, info in new_data["recent_artists"].items():
        new_artist = RecentArtists(
            user_stats_id=user_stats.id,
            artist=artist_name,
            img_url=info['img_url'],
            spotify_url=info['spotify_url'],
            href=info['href']
        )
        db.session.add(new_artist)

    for artist_name, info in new_data["medium_artists"].items():
        new_artist = MediumArtists(
            user_stats_id=user_stats.id,
            artist=artist_name,
            img_url=info['img_url'],
            spotify_url=info['spotify_url'],
            href=info['href']
        )
        db.session.add(new_artist)

    for artist_name, info in new_data["all_time_artists"].items():
        new_artist = AllTimeArtists(
            user_stats_id=user_stats.id,
            artist=artist_name,
            img_url=info['img_url'],
            spotify_url=info['spotify_url'],
            href=info['href']
        )
        db. session.add(new_artist)

    for track_name, info in new_data["recent_tracks"].items():
        new_track = RecentTracks(
            user_stats_id=user_stats.id,
            song=track_name,
            track_id = info['track_id'],
            album_art_img_url = info['album_art_img_url'],
            preview_url = info['preview_url'],
            spotify_url = info['spotify_url'],
            href = info['href'],
        )
        db.session.add(new_track)

    for track_name, info in new_data["medium_tracks"].items():
        new_track = MediumTracks(
            user_stats_id=user_stats.id,
            song=track_name,
            track_id = info['track_id'],
            album_art_img_url = info['album_art_img_url'],
            preview_url = info['preview_url'],
            spotify_url = info['spotify_url'],
            href = info['href'],
        )
        db.session.add(new_track)

    for track_name, info in new_data["all_time_tracks"].items():
        new_track = AllTimeTracks(
            user_stats_id=user_stats.id,
            song=track_name,
            track_id = info['track_id'],
            album_art_img_url = info['album_art_img_url'],
            preview_url = info['preview_url'],
            spotify_url = info['spotify_url'],
            href = info['href'],
        )
        db.session.add(new_track)

    db.session.commit()


def get_db_genres(user_id, time_range):
    # param user_id: user.id 
    # param time_range: 'r' for recent genres, 'a' for all time genres, 'm' for medium term genres

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
    elif time_range == 'm':
        if user_stats:
            medium_genres = MediumGenres.query \
                            .filter_by(user_stats_id=user_stats.id) \
                            .order_by(MediumGenres.id.asc()) \
                            .all()
        
            for genre in medium_genres:
                genre_dict[genre.genre] = genre.genre_count
            return genre_dict
        else:
            return {}
    else:
        # error handling
        raise ValueError("Incorrect time_range input. Expected 'r' for recent, 'm' for medium, or 'a' for all time genres.")

def get_db_artists(user_id, time_range):
    # param user_id: user.id 
    # param time_range: 'r' for recent artists, 'a' for all time artists, 'm' for medium term artists

    user_stats = UserStats.query.filter_by(user_id=user_id).first()
    artists = []
    if time_range == 'r':
        if user_stats:
            recent_artists = RecentArtists.query \
                            .filter_by(user_stats_id=user_stats.id) \
                            .order_by(RecentArtists.id.asc()) \
                            .all()
        
            for artist in recent_artists:
                artists.append(
                    {
                        'name': artist.artist,
                        'img_url': artist.img_url,
                        'spotify_url': artist.spotify_url,
                        'href': artist.href,
                    }
                )
            
    elif time_range == 'a':
        if user_stats:
            all_time_artists = AllTimeArtists.query \
                            .filter_by(user_stats_id=user_stats.id) \
                            .order_by(AllTimeArtists.id.asc()) \
                            .all()
        
            for artist in all_time_artists:
                artists.append(
                    {
                        'name': artist.artist,
                        'img_url': artist.img_url,
                        'spotify_url': artist.spotify_url,
                        'href': artist.href,
                    }
                )
            
    elif time_range == 'm':
        if user_stats:
            medium_artists = MediumArtists.query \
                            .filter_by(user_stats_id=user_stats.id) \
                            .order_by(MediumArtists.id.asc()) \
                            .all()
        
            for artist in medium_artists:
                artists.append(
                    {
                        'name': artist.artist,
                        'img_url': artist.img_url,
                        'spotify_url': artist.spotify_url,
                        'href': artist.href,
                    }
                )
            
    else:
        # error handling
        raise ValueError("Incorrect time_range input. Expected 'r' for recent, 'm' for medium, or 'a' for all time artists.")
    return artists

def get_db_tracks(user_id, time_range):
    # param user_id: user.id 
    # param time_range: 'r' for recent tracks, 'a' for all time tracks, 'm' for medium term tracks

    user_stats = UserStats.query.filter_by(user_id=user_id).first()
    tracks = []
    if time_range == 'r':
        if user_stats:
            recent_tracks = RecentTracks.query \
                            .filter_by(user_stats_id=user_stats.id) \
                            .order_by(RecentTracks.id.asc()) \
                            .all()
        
            for track in recent_tracks:
                tracks.append(
                    {
                        'name': track.song,
                        'track_id': track.track_id,
                        'album_art_img_url': track.album_art_img_url,
                        'preview_url': track.preview_url,
                        'spotify_url': track.spotify_url,
                        'href': track.href
                    }
                )
            return tracks
        else:
            return []
    elif time_range == 'a':
        if user_stats:
            all_time_tracks = AllTimeTracks.query \
                            .filter_by(user_stats_id=user_stats.id) \
                            .order_by(AllTimeTracks.id.asc()) \
                            .all()
        
            for track in all_time_tracks:
                tracks.append(
                    {
                        'name': track.song,
                        'track_id': track.track_id,
                        'album_art_img_url': track.album_art_img_url,
                        'preview_url': track.preview_url,
                        'spotify_url': track.spotify_url,
                        'href': track.href
                    }
                )
            return tracks
        else:
            return []
    elif time_range == 'm':
        if user_stats:
            medium_tracks = MediumTracks.query \
                            .filter_by(user_stats_id=user_stats.id) \
                            .order_by(MediumTracks.id.asc()) \
                            .all()
        
            for track in medium_tracks:
                tracks.append(
                    {
                        'name': track.song,
                        'track_id': track.track_id,
                        'album_art_img_url': track.album_art_img_url,
                        'preview_url': track.preview_url,
                        'spotify_url': track.spotify_url,
                        'href': track.href
                    }
                )
            return tracks
        else:
            return []
    else:
        # error handling
        raise ValueError("Incorrect time_range input. Expected 'r' for recent, 'm' for medium, or 'a' for all time tracks.")
    
def get_db_median_values(user_id, time_range):
    # param user_id: user.id
    # param time_range: 'r' for recent values, 'a' for all time values, 'm' for medium term values

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
    elif time_range == 'm':
        median_values["tempo"] = user_stats.tempo_m
        median_values["loudness"] = user_stats.loudness_m
        median_values["acousticness"] = user_stats.acousticness_m
        median_values["danceability"] = user_stats.danceability_m
        median_values["valence"] = user_stats.valence_m
        median_values["energy"] = user_stats.energy_m
        median_values["speechiness"] = user_stats.speechiness_m
        median_values["popularity"] = user_stats.popularity_m
        median_values["variance"] = user_stats.variance_m
        
        return median_values
    else:
        # error handling
        raise ValueError("Incorrect time_range input. Expected 'r' for recent, 'm' for medium term, or 'a' for all time values.")

