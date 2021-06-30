#import spotify_data_generator
import festival_scraper
import json

def create_artist_reference(f_data):
    # create a db mapping artists to festivals
    artist_db = {}
    for f in f_data:
        for a in f_data[f]['lineup']:
            if a not in artist_db.keys():
                artist_db[a] = []
            artist_db[a].append(f)
    with open('artist_list.json', 'w') as fp:
        json.dump(artist_db, fp)

with open('festival_list.json', 'r') as fp:
    festival_data = json.load(fp)
create_artist_reference(festival_data)

