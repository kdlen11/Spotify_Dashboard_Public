import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer, models
import torch

from src.fetch_top_tracks.spotify_api_call import RealAPI, DummyAPI
from src.fetch_top_tracks.app import MyApp
from src.fetch_song_lyrics.fetch_lyrics import fetch_dummy_lyrics, fetch_real_lyrics

def title_word_filter(input_title, rec_title):
    """
    Returns True if a recommended song should be filtered out
    because it shares any word in its title in common with input_title (case-insensitive).
    """
    input_words = set(input_title.lower().split())
    rec_words = set(rec_title.lower().split())
    return not input_words.isdisjoint(rec_words)  # True if they share any word


def rec_one_song(lyrics, input_title, top_k = 3):

    recs = []

    """
    Generates k recommendations for one inputted song, based on our embedding model of choice.
    Selects songs from our existing internal dataset by finding those that are most similar in the embedding space.
    """
    
    model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

    npz = np.load("src/model_embeddings/song_embeddings_miniLM.npz")
    emb_matrix = npz['embeddings']
    df = pd.read_csv("src/model_embeddings/spotify_millsongdata.csv")

    new_embedding = model.encode(lyrics, convert_to_numpy=True)
    emb_norms = np.linalg.norm(emb_matrix, axis=1)
    query_norm = np.linalg.norm(new_embedding)

    sims = emb_matrix @ new_embedding / (emb_norms * query_norm)

    top_indices = np.argsort(sims)[-15:][::-1]   # sorted highest → lowest, number 15 is random but probs good enough

    for idx in top_indices:
        row = df.iloc[idx]
        candidate_title = row['song']

        # skip if any word overlaps with input_title
        if title_word_filter(input_title, candidate_title):
            continue

        rec_info = {'title': row['song'], 'artist': row['artist']}
        recs.append(rec_info)
        
        if len(recs) >= top_k:
            break


    return recs

def store_rec_data(force_dummy = True):

    all_rec_data = {'songs':[]}

    if force_dummy == True:
        api = MyApp(force_dummy = True)
        df = api.fetch_data()
        for index, row in df.iterrows():

            # this code only works for the five dummy .txt files that exist in our code, 
            # and the hard-coded df that correlates to those songs, called 'backup_top_tracks.csv' within src/fetch_top_tracks.
            # change any of those files at your own expense!

            safe_title = row["title"].lower().replace(" ", "_").replace("'", "")
            lyrics = fetch_dummy_lyrics(safe_title)

            recs = rec_one_song(lyrics=lyrics, input_title=row["title"], top_k=3)

            song_entry = {
            "title": row["title"],
            "artist": row["artist"],
            "recs": recs 
            }

            all_rec_data['songs'].append(song_entry)


    elif force_dummy == False:
        api = MyApp(force_dummy = False)
        df = api.fetch_data()

        recs = [
                { "title": "Never Gonna Give You Up", "artist": "Rick Astley" },
                { "title": "Never Gonna Give You Up", "artist": "Rick Astley" },
                { "title": "Never Gonna Give You Up", "artist": "Rick Astley" }
            ]

        for index, row in df.iterrows():

            song_entry = {
                "title": row['title'],
                "artist": row['artist'],
                "recs": recs
            }

            all_rec_data['songs'].append(song_entry)

    else:
        print("you must use either 'dummy' or 'real' mode.")

    return all_rec_data