def fetch_real_lyrics(track_name = "N/A"):
    """
    this is where we would put our code that fetches the lyrics of a single song,
    if such an API existed for our use.
    """
    return None

def fetch_dummy_lyrics(track_name:str):
    """
    this is the function we will use in order to fetch the dummy lyrics 
    that we have stored in our repository for testing purposes.    
    """
    path_to_dummy_lyrics = f"src/fetch_song_lyrics/dummy_lyrics/{track_name}.txt"

    with open(path_to_dummy_lyrics, 'r', encoding='utf-8') as file:
        lyrics = file.read()

    return lyrics