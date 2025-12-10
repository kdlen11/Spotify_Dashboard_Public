from src.fetch_recommendations.make_rec import store_rec_data
from src.generate_dashboard.dashboard import generate_dashboard
from src.fetch_top_tracks.app import MyApp

from typing import Callable
import tkinter as tk
import webbrowser
import os
import threading
import tkinter.ttk as ttk

class MyInterface_Tk:
    '''
    This class creates the user interface.
    It does none of the API calls and song ebeddings.
    '''

    BTN_HEIGHT  = 5
    BTN_WIDTH   = 30
    BTN_WRAPLEN = 150 

    def __init__(self,
                 geometry = '600x200'
                 ):

        # Layout the figure and the buttons
        self.configure_main_window(geometry)

        # The mainloop() runs the application
        self.main_window.mainloop()
        return

    def configure_main_window(self,
                              geometry: str
                              ):
        
        # Function defines and places all the buttons.
        self.main_window = tk.Tk()
        self.main_window.geometry(geometry)
        self.main_window.title('Spotify Dashboard and Song Suggestion')

        # Create the interface area,
        # which will be a container for the plot and the buttons
        self.interface_area = tk.Frame(self.main_window)

        ###Labels
        self.__create_label(
        text="Welcome to the Spotify User Listening Dashboard.\nClick below to see your top songs and generate song recommendations.",
        row=0,
        column=0,
        columnspan=2
        )

        ### Buttons
        self.button_spotify_login = \
            self.__create_button(text = 'Log in with Spotify',
                                    row = 1,
                                    column = 0,
                                    command = self.spotify_api_call
                                    )
        
        self.button_no_spotify = \
            self.__create_button(text = "I don't have Spotify,\nshow me an example",
                                    row = 1,
                                    column = 1,
                                    command = self.dummy_api_call
                                    )
        
        self.interface_area.pack()
        self.check_for_key()
        return
    
    def check_for_key(self) -> bool:
        """
        This function checks for API keys in the correct format before any calls are made.
        If the keys are present, .button_spotify_login will be activatied,
        otherwise, it will be deactivated and the user will be prompted to create keys.
        """
        #create an instance of the app
        app = MyApp()

        #attempt to load the key, if its there, do nothing, if not, disable the button
        key_present = app.load_key()
        if key_present:
            print('key found')
            return
        else:
            self.button_spotify_login.config(state="disabled")
            self.button_spotify_login.config(text="Log in with Spotify\n(To access this, please see ReadMe for key.json file creation)")

            print('key not found, button disabled')
            return
    
    def __create_button(self,
                        text:       str,
                        row:        int,
                        column:     int,
                        command:    Callable,
                        master:     tk.Frame    = None, # Default to self.interface_area
                        wraplength: int         = BTN_WRAPLEN,
                        height:     int         = BTN_HEIGHT,
                        width:      int         = BTN_WIDTH,
                        ) -> tk.Button:
        if master is None:
            master = self.interface_area
        
        button = tk.Button(master       = master,
                           command      = command,
                           text         = text,
                           wraplength   = wraplength,
                           height       = height,
                           width        = width
                           )
        button.grid(row=row, column=column)
        return button
    
    def __create_label(self,
                   text: str,
                   row: int,
                   column: int,
                   master: tk.Frame = None,
                   wraplength: int = 500,
                   justify: str = "center",
                   font: tuple = ("Helvetica", 12),
                   columnspan: int = 1,
                   pady: tuple = (10, 10)
                   ) -> tk.Label:
        if master is None:
            master = self.interface_area

        label = tk.Label(master=master,
                        text=text,
                        wraplength=wraplength,
                        justify=justify,
                        font=font)
        label.grid(row=row, column=column, columnspan=columnspan, pady=pady)
        return label
    
    def dummy_api_call(self):
        """
        This function completes the entire pipeline of pulling data and creating a dashboard
        when the user doesn't have spotify or doesn't have their keys set up.
        This function will create an instance of MyApp, 
        forcing dummy to be true and pulling backup songs.
        It pops up a progress bar while the embeddings are being created
        and automatically opens the dashboard when it is completed.
        """

        # Disable buttons
        self.button_spotify_login.config(state="disabled")
        self.button_no_spotify.config(state="disabled")

        # Create popup window
        popup = tk.Toplevel(self.main_window)
        popup.title("Generating Recommendations")
        popup.geometry("350x120")
        tk.Label(popup, text="Song recommendations are being generated...",
                font=("Helvetica", 12)).pack(pady=10)

        # Progress bar
        progress = ttk.Progressbar(popup, mode="indeterminate")
        progress.pack(fill="x", padx=20, pady=10)
        progress.start(10)

        def run_task():
            try:
                recs = store_rec_data(force_dummy = True)
            finally:

                # All UI updates must be sent back to the Tk main thread
                def finish():
                    progress.stop()
                    popup.destroy()

                    generate_dashboard(recs, force_dummy= True)

                    file_path = os.path.join("src/generate_dashboard", "song_report.html")
                    abs_path = os.path.abspath(file_path)
                    webbrowser.open(f"file:///{abs_path}")

                    # Now it's safe to destroy the window
                    self.main_window.destroy()

                # Schedule back on main thread
                self.main_window.after(0, finish)

        # Run worker in background thread
        threading.Thread(target=run_task, daemon=True).start()

        return

    def spotify_api_call(self):
        """
        This function completes the entire pipeline of pulling data 
        and creating a dashboard when the user has spotify.
        This function will create an instance of MyApp, 
        forcing dummy to be false and prompting the user to log in with spotify.
        The user has 30 seconds to log in and if the process is not completed,
        an error is thrown and the user is prompted to use the backup data.
        If the login is sucessful, the dashboard will open automatically.
        """

        # Disable buttons so user can't click again
        self.button_spotify_login.config(state="disabled")
        self.button_no_spotify.config(state="disabled")

        #Set up so the window is still responsive
        def run_task():
            try:
                # Run long task in background thread
                recs = store_rec_data(force_dummy=False)
                success = True
            except Exception as e:
                print("Error during Spotify API call:", e)
                success = False
                recs = None   # to avoid undefined variable
            finally:
                def finish():
                    if success:
                        # Successful: generate dashboard
                        generate_dashboard(recs, force_dummy=False)

                        file_path = os.path.join("src/generate_dashboard", "song_report.html")
                        abs_path = os.path.abspath(file_path)
                        webbrowser.open(f"file:///{abs_path}")

                        self.main_window.destroy()

                    else:
                        # Error: show the custom error window
                        self.show_error_window()
                        # Re-enable buttons so user can choose dummy example
                        self.button_no_spotify.config(state="normal")
                        #self.button_spotify_login.config(state="normal")

                # schedule back onto the Tkinter main thread
                self.main_window.after(0, finish)

        threading.Thread(target=run_task, daemon=True).start()


    def show_error_window(self):
        """
        This function is called when there is an error logging into spotify.
        It creates a pop up window that suggests the user use the alternative button.
        """
        new_window = tk.Tk()
        new_window.geometry("500x150")
        new_window.title("Error")
        error_message = (
            "There has been an error logging into Spotify.\n"
            "Please select the alternative button to see an example of the dashboard."
        )

        label = tk.Label(new_window, text=error_message, wraplength=450, justify="center", font=("Arial", 12))
        label.pack(expand=True, pady=30)
