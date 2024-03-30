# Spotify extraction functions

def get_tracks_info(top_tracks):
    # returns nested dictionary with top tracks and associated info
    tracks = {}
    for item in top_tracks:
        tracks[item['name']] = {
            'track_id': item['id'],
            'album_art_img_url': item['album']['images'][0]['url'] if item['album']['images'] else None,
            'preview_url': item.get('preview_url', None),
            'spotify_url': item['external_urls']['spotify'],
            'href': item['href']
        }
    return tracks

def get_artists_info(top_artists):
    # returns nested dictionary with top 10 artists and associated info  
    # outer dictionary: (key, value) --> (artist, info dict)
    # inner dictionary: keys --> img_url, genres, spotify_url, href, popularity 
    artists = {}
    for item in top_artists:
        artists[item['name']] = {
            'img_url': item['images'][0]['url'] if item['images'] else None,  
            'genres': item['genres'],
            'spotify_url': item['external_urls']['spotify'],
            'href': item['href'],
            'popularity': item['popularity']
        }
    return artists

def get_genre_count(artists_info):
    # returns dictionary of genres and their respective count (calculated based on artists), sorted by count
    # dictionary: (key, value) --> (genre, count)
    all_genres = {}
    for artist, info in artists_info.items():
        for genre in info['genres']:
            if genre in all_genres:
                all_genres[genre] += 1  
            else:
                all_genres[genre] = 1
    
    all_genres = {k: v for k, v in sorted(all_genres.items(), key=lambda item: item[1], reverse=True)}
    
    return all_genres

def get_popularity(top_artists):
    # returns median popularity score for top 10 artists
    popularity_scores = []
    for item in top_artists:
        popularity_scores.append(item['popularity'])

    #print(popularity_scores)

    median = find_median(popularity_scores)
    
    return median

def split_list_into_chunks(lst, chunk_size):
    """Yield successive chunk_size chunks from lst."""
    for i in range(0, len(lst), chunk_size):
        yield lst[i:i + chunk_size]


def get_audio_features_tracks(track_info, spotify):
    track_ids = [info['track_id'] for track, info in track_info.items()]

    track_chunks = list(split_list_into_chunks(track_ids, 50))

    tempo_scores = []
    loudness_scores = []
    acousticness_scores = []
    danceability_scores = []
    valence_scores = []
    energy_scores = []
    speechiness_scores = []

    for chunk in track_chunks:
        audio_features_list = spotify.audio_features(chunk)

        for audio_features in audio_features_list:
            if audio_features:
                tempo_scores.append(audio_features.get('tempo', 0))
                loudness_scores.append(audio_features.get('loudness', 0))
                acousticness_scores.append(audio_features.get('acousticness', 0))
                danceability_scores.append(audio_features.get('danceability', 0))
                valence_scores.append(audio_features.get('valence', 0))
                energy_scores.append(audio_features.get('energy', 0))
                speechiness_scores.append(audio_features.get('speechiness', 0))

    median_tempo_pre = round(find_median(tempo_scores),ndigits=2)
    median_loudness_pre = round(find_median(loudness_scores),ndigits=2)
    median_acousticness = round(find_median(acousticness_scores), ndigits=2) * 100
    median_danceability = round(find_median(danceability_scores), ndigits=2)* 100
    median_valence = round(find_median(valence_scores), ndigits=2)* 100
    median_energy = round(find_median(energy_scores), ndigits=2)* 100
    median_speechiness = round(find_median(speechiness_scores), ndigits=2)* 100

    # Normalizing process, others normalized before
    median_tempo = median_tempo_pre / 2
    median_loudness = abs((abs(median_loudness_pre) - 10) * 33)
    if median_loudness > 100:
        median_loudness = 100
    median_values = {
        'tempo': median_tempo, 
        'loudness': median_loudness, 
        'acousticness': median_acousticness, 
        'danceability': median_danceability, 
        'valence': median_valence, 
        'energy': median_energy, 
        'speechiness': median_speechiness
    }
    
    return median_values

def get_variance():
    #TODO
    return 0

def find_median(numbers):
    numbers.sort()
    
    middle = len(numbers) // 2
    
    if len(numbers) % 2 != 0:
        return numbers[middle]
    else:
        return (numbers[middle - 1] + numbers[middle]) / 2.0
