import spotipy
from spotipy.oauth2 import SpotifyOAuth
import abc
import pandas as pd
import threading


DUMMY_PATH = 'resources/dummy_data.json'


class BaseAPI(abc.ABC):
    '''
    All classes inheriting from BaseAPI must define an implementation 
    of all of its abstract methods. In this case, just a fetch_data() function.

    The benefit of using ABC is just so that an error will be thrown if we forget to
    define a concrete implementation of the abstract methods in a child class.
    '''
    @abc.abstractmethod
    def fetch_data(self) -> dict:
        pass

class DummyAPI(BaseAPI):
    def __init__(self):
        self.key = None
        return
        
    def fetch_data(self) -> dict:
        '''
        The DummyAPI returns sample data stored locally.
        '''

        top_tracks = pd.read_csv('src/fetch_top_tracks/backup_top_tracks.csv')
        return top_tracks

class RealAPI(BaseAPI):
    def __init__(self, client_id, client_secret, redirect_uri):
        self.id = client_id
        self.secret = client_secret
        self.uri = redirect_uri
        return

    def fetch_data(self) -> dict:
        '''
        The RealAPI fetches data from a user's Spotify account.
        It requires a client ID and secret as well as the user be added to the project
        (see ReadMe).
        '''

        print('fetching data from real api')
        SCOPE = "user-library-read user-top-read"

        auth_manager = SpotifyOAuth(
            client_id=self.id,
            client_secret=self.secret,
            redirect_uri=self.uri,
            scope=SCOPE,
            open_browser=True
        )

        token_info = {}

        def get_token():
            nonlocal token_info
            token_info = auth_manager.get_access_token(as_dict=True)

        # Run in a thread with timeout
        t = threading.Thread(target=get_token)
        t.daemon = True
        t.start()
        #limit timeout to 30 seconds
        t.join(timeout = 30)

        # if there's a timeout of we didn't get the token, raise an error 
        # (this will be caught in the ui code)
        if t.is_alive() or not token_info or "access_token" not in token_info:
            print("Login timed out or failed.")
            raise Exception('Login timed out of failed.')

        sp = spotipy.Spotify(auth_manager=auth_manager)
        top = sp.current_user_top_tracks(limit=5, time_range='short_term')
        return pd.DataFrame([
            {"ranking": idx+1, "title": item["name"], "artist": item["artists"][0]["name"]}
            for idx, item in enumerate(top["items"])
        ])
    
class BrokenAPI(BaseAPI):
    '''
    This class will throw an error upon instantiation,
    because it does not define a fetch_data method.
    '''

    def __init__(self):
        print('This will never print')
        return
