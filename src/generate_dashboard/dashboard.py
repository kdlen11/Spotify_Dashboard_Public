import json
import os
import plotly.express as px
import pandas as pd


def generate_dashboard(songs_json, force_dummy = True):
    data = songs_json
    songs = data["songs"]

    # ----------------------------------------
    # Create Summary Chart
    # ----------------------------------------
    df = pd.DataFrame({
        "Title": [s["title"] for s in songs],
        "Recommendations": [len(s["recs"]) for s in songs]
    })

    # ----------------------------------------
    # Generate HTML Song Cards
    # ----------------------------------------
    html_parts = []

    for song in songs:
        title = song["title"]
        artist = song["artist"]

        rec_items = "".join(
            f"<div style = 'margin-top:5px'>{rec['title']} — {rec['artist']}</div>"
            for rec in song["recs"]
        )

        card_html = f"""
        <div style="
            padding: 18px;
            background: white;
            border-radius: 12px;
            box-shadow: 0 3px 10px rgba(0,0,0,0.12);
            margin-bottom: 25px;
            font-family: Arial;
        ">
            <h2 style="margin: 0 0 3px 0; color:#21498C">{title}</h2>
            <h4 style="opacity: 0.7; margin-top:4px; color:#ab7de3">{artist}</h4>

            <h3 style = "margin: -3 0 0 0;">Recommendations</h3>
            {rec_items}
        </div>
        """
        html_parts.append(card_html)

    # adding Rick Roll audio for fake recommendations
    audio_html = ""
    notice_something = ""
    if force_dummy == False:
        audio_html = """
            <h3 style = "font-family: 'Helvetica'"> Play Me </h3>
            <audio autoplay controls>
                <source src="rick_roll.mp3" type="audio/mpeg">
            </audio>"""
        notice_something = """
            <h3 style = "font-family: 'Helvetica'">
                Notice anything strange about your recommendations?
            </h3>

            <h4 style = "opacity: 0.7; font-family: 'Helvetica'"> 
                Because your top songs are pulled from your native, actual Spotify account, we have no way of 
                finding their lyrics due to copyright laws, meaning we can't generate similar songs.
            </h4>
            
            <h4 style = "opacity: 0.7; font-family: 'Helvetica'"> 
                If you want to see an example of actually generated recommendations, please select <i>I don't 
                have a Spotify account</i> on the startup menu.
            </h4>
            """


    # Wrap HTML
    full_html = f"""
    <html>
    <head>
        <title>Song Recommendation Report</title>
    </head>
    <body style="background:#fcf5e8; padding:20px; max-width:950px; margin:0 auto; text-align:center">
        {audio_html}
        <h1 style="text-align:center; font-family: 'Helvetica', sans-serif;">
            Your Top Spotify Song Recommendations
        </h1>
        <h2 style="text-align:center; font-family: 'Helvetica', sans-serif; color: #555;">
            Your top 5 Spotify songs for the past month:
        </h2>
        <h2 style="text-align:center; font-family: 'Helvetica', sans-serif; color: #555;">
            and 3 songs we think you should listen to, based on each.
        </h2>
        {''.join(html_parts)}
        {notice_something}
    </body>
    </html>
    """

    # save output to that same directory

    file_path = "src/generate_dashboard/song_report.html"

    # Delete old file if it exists
    if os.path.exists(file_path):
        os.remove(file_path)

    # Write new file
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(full_html)

    print("Saved:", file_path)

    return None