# Spotify extraction functions

def get_tracks_info(top_tracks):
    # returns nested dictionary with top tracks and associated info
    tracks = []
    for item in top_tracks:
        # If there are multiple artists, this will join their names with a comma. 
        # If there's only one artist, it just returns that name.
        artist_names = ', '.join([artist['name'] for artist in item['artists']])

        tracks.append(
            {
                'name': item['name'],
                'album_art_img_url': item['album']['images'][0]['url'] if item['album']['images'] else None,
                'preview_url': item.get('preview_url', None),
                'spotify_url': item['external_urls']['spotify'],
                'href': item['href'],
                'track_id': item['id'],
                'artist': artist_names  # Now 'artist' will contain a string of artist names, possibly more than one
            }
        )
    return tracks

def get_tracks_info_batch(top_tracks):
    # returns nested dictionary with top tracks and associated info
    tracks = {}
    priority = 0
    for item in top_tracks:
        track = item['track']  # Access the nested track object
        tracks[track['name']] = {
            'track_id': track['id'],
            'album_art_img_url': track['album']['images'][0]['url'] if track['album']['images'] else None,
            'preview_url': track.get('preview_url', None),
            'spotify_url': track['external_urls']['spotify'],
            'href': track['href'],
            'priority': priority
        }
        priority += 1
    return tracks


def get_artists_info(top_artists):
    # returns nested dictionary with top 10 artists and associated info  
    # outer dictionary: (key, value) --> (artist, info dict)
    # inner dictionary: keys --> img_url, genres, spotify_url, href, popularity 
    artists = []
    priority = 0
    for item in top_artists:
        artists.append(
            {
                'name': item['name'],
                'img_url': item['images'][0]['url'] if item['images'] else None,  
                'genres': item['genres'],
                'spotify_url': item['external_urls']['spotify'],
                'href': item['href'],
                'popularity': item['popularity'],
            }
        )
    return artists

def get_genre_count(artists_info):
    # returns dictionary of genres and their respective count (calculated based on artists), sorted by count
    # dictionary: (key, value) --> (genre, count)
    all_genres = {}
    for artist in artists_info:
        for genre in artist['genres']:
            if genre in all_genres:
                all_genres[genre] += 1  
            else:
                all_genres[genre] = 1
    
    all_genres = {k: v for k, v in sorted(all_genres.items(), key=lambda item: item[1], reverse=True)}
    
    return all_genres

def get_genre_count_batch(artists_info):
    # returns dictionary of genres and their respective count (calculated based on artists), sorted by count
    # dictionary: (key, value) --> (genre, count)
    all_genres = {}
    for artist, info in artists_info:
        for genre in info['genres']:
            if genre in all_genres:
                all_genres[genre] += 1  
            else:
                all_genres[genre] = 1
    
    all_genres = {k: v for k, v in sorted(all_genres.items(), key=lambda item: item[1], reverse=True)}
    
    return all_genres

def get_artist_genres_batch(response):
    # response is the dictionary returned from sp.artists(chunk)
    artists = {}
    # Access the list of artists with response['artists']
    for item in response['artists']:
        artists[item['name']] = item['genres']
    return artists


def get_genre_count_batch(genres_list):
    # genres_list is a list of dictionaries
    # Each dictionary maps artist names to their genres
    all_genres = {}
    for genres_dict in genres_list:  # Iterate over each dictionary in the list
        for artist, genres in genres_dict.items():  # Now iterating over each artist-genres pair in the dictionary
            for genre in genres:  # Iterate over genres of the current artist
                if genre in all_genres:
                    all_genres[genre] += 1
                else:
                    all_genres[genre] = 1

    # Sorting genres by count in descending order
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
    track_ids = [track['track_id'] for track in track_info]

    track_chunks = list(split_list_into_chunks(track_ids, 50))

    tempo_scores = []
    loudness_scores = []
    acousticness_scores = []
    danceability_scores = []
    valence_scores = []
    energy_scores = []
    speechiness_scores = []

    for chunk in track_chunks:
        chunk_as_string = ".".join(chunk)
        print(len(chunk))
        audio_features_list = spotify.audio_features(chunk)
        print("first chunk successfully extracted")

        for audio_features in audio_features_list:
            if audio_features:
                tempo_scores.append(audio_features.get('tempo', 0))
                loudness_scores.append(audio_features.get('loudness', 0))
                acousticness_scores.append(audio_features.get('acousticness', 0))
                danceability_scores.append(audio_features.get('danceability', 0))
                valence_scores.append(audio_features.get('valence', 0))
                energy_scores.append(audio_features.get('energy', 0))
                speechiness_scores.append(audio_features.get('speechiness', 0))

    median_tempo_pre = round(round(find_median(tempo_scores),ndigits=4), ndigits=2)
    median_loudness_pre = round(round(find_median(loudness_scores),ndigits=4), ndigits=2)
    median_acousticness = round(round(find_median(acousticness_scores), ndigits=4) * 100, ndigits=2)
    median_danceability = round(round(find_median(danceability_scores), ndigits=4)* 100, ndigits=2)
    median_valence = round(round(find_median(valence_scores), ndigits=4)* 100, ndigits=2)
    median_energy = round(round(find_median(energy_scores), ndigits=4)* 100, ndigits=2)
    median_speechiness = round(round(find_median(speechiness_scores), ndigits=4)* 1000, ndigits=2) #This is not always right

    # Normalizing process, others normalized before
    median_tempo = ((median_tempo_pre - 120)*2.5) + 50
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
