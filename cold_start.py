import pandas as pd
import datetime

# from random import sample
# import data

data = pd.read_csv('data/data.csv')

def range_years(dobyear):
    currentdate = datetime.datetime.now()
    if dobyear >= 1960:
        year1 = dobyear - 10
        year2 = dobyear + 30
        if (dobyear + 30) > currentdate.year:
            year1 = dobyear - 10
            year2 = 2022
    else:
        year1=1950
        year2=1980
    years = {'year1': year1, 'year2': year2}
    return years

# 1950-2022
from random import sample
def get_artists(gen, years):
    a = data[(data['genre'] == gen) & (data['year'] >= years['year1']) & (data['year'] <= years['year2'])]
    a_unique=a.drop_duplicates()
    artist = a_unique['artist'].drop_duplicates()
    artist_list = artist.to_list()
    verified_artist = []
    for i in artist_list:
        dat = a_unique.loc[(data['artist'] == i) & (data['year'] >= years['year1']) & (data['year'] <= years['year2'])]
        songs=dat['name'].to_list()
        if(len(songs)>=5):
            artsy={
                'artist_name':i,
                'artist_songl':len(songs)
            }
            verified_artist.append(artsy)
    if(len(verified_artist)>=5):
        artists = sample(verified_artist, 5)
    else:
        artists = verified_artist
    art = {
        'artist': artists
    }
    return art


def get_tracks(attribute, parameter, years):
    if years==None:
        if parameter=='artist': 
            a = data.loc[(data['artist'] == attribute)]    
        elif parameter=='genre':
            a = data.loc[data['genre']==attribute]
    elif parameter=='artist':
        a = data.loc[(data['artist'] == attribute) & (data['year'] >= years['year1']) & (data['year'] <= years['year2'])]
    if a is not None:
        ar = a.sample(n=20, replace=True)
        tracks = ar.drop_duplicates()
        var = len(tracks)
        name_list = tracks['name'].to_list()
        year_list = tracks['year'].to_list()
        artist_list = tracks['artist'].to_list()
        url_list = tracks['url'].to_list()
        uri_list = tracks['uri'].to_list()
        songs_list = []
        for i in range(var):
            songs = {
                'name': name_list[i],
                'artist_name': artist_list[i],
                'year': year_list[i],
                'External_Link': url_list[i],
                'uri': uri_list[i]
            }
            songs_list.append(songs)
    return songs_list

def more_songs(uri):
    #urilist=uris['key']
    songs_list = []
    for i in uri:
        a = data.loc[data['uri'] == i]
        listed = a.values.tolist()
        # print(listed[0][1])
        dat = {'name': listed[0][0], 'year': listed[0][1]}
        songs_list.append(dat)
    return songs_list

def uri_data(uri_list):
    songs_list = []
    for i in uri_list:
        a = data.loc[data['uri'] == i]
        listed = a.values.tolist()
        #print(listed[0][1])
        dat = {'External_Link':listed[0][2],'artist':listed[0][6],'name': listed[0][0], 'year': listed[0][1],'uri':listed[0][3]}
        songs_list.append(dat)
    return songs_list

#years={'year1':1988,'year2':2020}
#print(get_artists('folk',years))
#print(get_tracks('Florence The Machine','artist',years))



#uri_list=["3fQLXoRwKQTnThncdMCqwG","1uwSOYXZoxgSqhn8FIkfH1"]
#print(uri_data(uri_list))
#[{'External_Link': 'https://open.spotify.com/track/3fQLXoRwKQTnThncdMCqwG', 'artist': 'Pérez Prado', 'name': 'Mambo No 5', 'year': 1950, 'uri': '3fQLXoRwKQTnThncdMCqwG'}, {'External_Link': 'https://open.spotify.com/track/1uwSOYXZoxgSqhn8FIkfH1', 'artist': 'Pérez Prado', 'name': 'Que Rico Mambo', 'year': 1950, 'uri': '1uwSOYXZoxgSqhn8FIkfH1'}]
