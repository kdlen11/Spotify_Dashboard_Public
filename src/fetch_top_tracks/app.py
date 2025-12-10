from src.fetch_top_tracks.spotify_api_call import DummyAPI, RealAPI
import json


KEY_FILE = 'src/fetch_top_tracks/key.json'
    
class MyApp:
    def __init__(self, force_dummy: bool = False):
        # If the API key was succesfully loaded,
        # use the RealAPI. If not, use the DummyAPI.
        if self.load_key() and not force_dummy:
            self.API = RealAPI(self.client_id, self.client_secret, self.client_uri)
        else:
            self.API = DummyAPI()

        # Either way, we have a functional fetch_data() method.
        self.fetch_data = self.API.fetch_data
        return

    def load_key(self) -> bool:
        '''
        Attempts to read the KEY from key.json.
        If succesful, returns True. If any errors occur, returns False.
        '''
        try:
            with open(KEY_FILE, 'r') as f:
                keys = json.load(f)
                self.client_id = keys["SPOTIFY_CLIENT_ID"]
                self.client_secret = keys["SPOTIFY_CLIENT_SECRET"]
                self.client_uri = keys["REDIRECT_URI"]

            return True
        except Exception as e:
            print(f'Could not load API key:\n\t{e}')
            return False
        
