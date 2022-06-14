import numpy as np
import pandas as pd

import spotipy as sp
from spotipy.oauth2 import SpotifyClientCredentials

spo = sp.Spotify(client_credentials_manager=SpotifyClientCredentials(client_id="9eb499b93cb44edebec7c7391b421341",
client_secret="03e2d9e4eb0746f98a4f7abddf2008b7"))


from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.pipeline import Pipeline

import warnings
warnings.filterwarnings("ignore")

data = pd.read_csv("data/data.csv")

song_cluster_pipeline = Pipeline([('scaler', StandardScaler()),('pca',PCA(n_components=2)),
                                  ('kmeans', KMeans(n_clusters=20,
                                   verbose=False))
                                 ], verbose=False)

X = data.select_dtypes(np.number)
number_cols = list(X.columns)
song_cluster_pipeline.fit(X)
song_cluster_labels = song_cluster_pipeline.predict(X)
data['cluster_label'] = song_cluster_labels

def find_song(name, year):
    dat=data[(data['name']==name) & (data['year']==year)]
    song_data=dat[['name','uri','valence', 'year', 'acousticness', 'danceability', 'duration_ms', 'energy', 'explicit',
 'instrumentalness', 'key', 'liveness', 'loudness', 'mode', 'track_popularity', 'speechiness', 'tempo','time_signature']]
    return song_data


from collections import defaultdict
from scipy.spatial.distance import cdist

number_cols = ['valence', 'year', 'acousticness', 'danceability', 'duration_ms', 'energy', 'explicit',
               'instrumentalness', 'key', 'liveness', 'loudness', 'mode', 'track_popularity', 'speechiness', 'tempo',
               'time_signature']


def get_song_data(song, spotify_data):
    try:
        song_data = spotify_data[(spotify_data['name'] == song['name'])
                                 & (spotify_data['year'] == song['year'])].iloc[0]
        return song_data

    except IndexError:
        return find_song(song['name'], song['year'])


def get_mean_vector(song_list, spotify_data):
    song_vectors = []

    for song in song_list:
        song_data = get_song_data(song, spotify_data)
        if song_data is None:
            print('Warning: {} does not exist in database'.format(song['name']))
            continue
        song_vector = song_data[number_cols].values
        song_vectors.append(song_vector)

    song_matrix = np.array(list(song_vectors))
    return np.mean(song_matrix, axis=0)


def flatten_dict_list(dict_list):
    flattened_dict = defaultdict()
    for key in dict_list[0].keys():
        flattened_dict[key] = []

    for dictionary in dict_list:
        for key, value in dictionary.items():
            flattened_dict[key].append(value)

    return flattened_dict


def recommend_songs(song_list, spotify_data, n_songs=10):
    metadata_cols = ['name', 'year', 'artist', 'uri', 'url']
    song_dict = flatten_dict_list(song_list)

    song_center = get_mean_vector(song_list, spotify_data)
    scaler = song_cluster_pipeline.steps[0][1]
    scaled_data = scaler.transform(spotify_data[number_cols])
    scaled_song_center = scaler.transform(song_center.reshape(1, -1))

    distances = cdist(scaled_song_center, scaled_data, 'cosine')

    index = list(np.argsort(distances)[:, :n_songs][0])

    rec_songs = spotify_data.iloc[index]
    rec_songs = rec_songs[~rec_songs['name'].isin(song_dict['name'])]
    return rec_songs[metadata_cols].to_dict(orient='records')

def catch_recommended(song_list):
    return recommend_songs(song_list,data)

song_list = [{'name': '#SELFIE', 'artist_name': 'The Chainsmokers', 'year': 2014, 'External_Link': 'https://open.spotify.com/track/1HOlb9rdNOmy9b1Fakicjo', 'uri': '1HOlb9rdNOmy9b1Fakicjo'}, {'name': 'This Feeling', 'artist_name': 'The Chainsmokers', 'year': 2018, 'External_Link': 'https://open.spotify.com/track/4NBTZtAt1F13VvlSKe6KTl', 'uri': '4NBTZtAt1F13VvlSKe6KTl'}, {'name': 'Kanye', 'artist_name': 'The Chainsmokers', 'year': 2014, 'External_Link': 'https://open.spotify.com/track/5brMyscUnQg14hMriS91ks', 'uri': '5brMyscUnQg14hMriS91ks'}, {'name': 'I Love U', 'artist_name': 'The Chainsmokers', 'year': 2022, 'External_Link': 'https://open.spotify.com/track/3MJE5DoCeAWP7cDbW9Hgm5', 'uri': '3MJE5DoCeAWP7cDbW9Hgm5'}, {'name': 'Takeaway', 'artist_name': 'The Chainsmokers', 'year': 2019, 'External_Link': 'https://open.spotify.com/track/3g0mEQx3NTanacLseoP0Gw', 'uri': '3g0mEQx3NTanacLseoP0Gw'}, {'name': 'Call You Mine', 'artist_name': 'The Chainsmokers', 'year': 2019, 'External_Link': 'https://open.spotify.com/track/2oejEp50ZzPuQTQ6v54Evp', 'uri': '2oejEp50ZzPuQTQ6v54Evp'}, {'name': "Don't Let Me Down", 'artist_name': 'The Chainsmokers', 'year': 2016, 'External_Link': 'https://open.spotify.com/track/1i1fxkWeaMmKEB4T7zqbzK', 'uri': '1i1fxkWeaMmKEB4T7zqbzK'}]
#print(data)
print(catch_recommended(song_list))

