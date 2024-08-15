import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import logging
import requests
from io import BytesIO

# Configure logging
logging.basicConfig(filename='spotify_errors.log', level=logging.ERROR,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Spotify credentials
SPOTIPY_CLIENT_ID = '60ea8712d5d54009be24890e3deaab8c'
SPOTIPY_CLIENT_SECRET = 'b3ab19a0e72e42b7a398b169196acb9d'
SPOTIPY_REDIRECT_URI = 'http://localhost:8888/callback'
SCOPE = 'user-read-playback-state user-modify-playback-state user-read-currently-playing user-read-playback-position app-remote-control'

# Initialize Spotipy
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=SPOTIPY_CLIENT_ID,
    client_secret=SPOTIPY_CLIENT_SECRET,
    redirect_uri=SPOTIPY_REDIRECT_URI,
    scope=SCOPE
))

def get_devices():
    try:
        devices = sp.devices()
        return devices['devices']
    except Exception as e:
        logging.error(f"Error getting devices: {e}")
        return []

def transfer_playback(device_id):
    try:
        sp.transfer_playback(device_id=device_id, force_play=True)
    except Exception as e:
        logging.error(f"Error transferring playback: {e}")

def update_ui():
    try:
        track_info = sp.current_playback()
        if track_info and track_info['is_playing']:
            track = track_info['item']
            album_art_url = track['album']['images'][0]['url']
            album_name = track['album']['name']
            track_name = track['name']
            artist_name = ', '.join(artist['name'] for artist in track['artists'])
            
            # Update UI components
            response = requests.get(album_art_url)
            response.raise_for_status()  # Raise an error for bad responses
            img_data = response.content
            img = Image.open(BytesIO(img_data))
            img = img.resize((150, 150), Image.ANTIALIAS)
            img = ImageTk.PhotoImage(img)

            album_art_label.config(image=img)
            album_art_label.image = img
            track_name_label.config(text=f"Track: {track_name}")
            artist_name_label.config(text=f"Artist: {artist_name}")
            album_name_label.config(text=f"Album: {album_name}")
    except Exception as e:
        logging.error(f"Error updating UI: {e}")

def skip_track():
    try:
        sp.next_track()
        update_ui()
    except Exception as e:
        logging.error(f"Error skipping track: {e}")

def pause_playback():
    try:
        sp.pause_playback()
        update_ui()
    except Exception as e:
        logging.error(f"Error pausing playback: {e}")

def resume_playback():
    try:
        sp.start_playback()
        update_ui()
    except Exception as e:
        logging.error(f"Error resuming playback: {e}")

def volume_up():
    try:
        volume = sp.current_playback()['device']['volume_percent']
        if volume < 100:
            sp.volume(volume + 10)
    except Exception as e:
        logging.error(f"Error increasing volume: {e}")

def volume_down():
    try:
        volume = sp.current_playback()['device']['volume_percent']
        if volume > 0:
            sp.volume(volume - 10)
    except Exception as e:
        logging.error(f"Error decreasing volume: {e}")

def select_device():
    devices = get_devices()
    if devices:
        for device in devices:
            if device['name'] == 'Raspberry Pi':  # Change to the name you've set for your Raspberry Pi
                device_id = device['id']
                transfer_playback(device_id)
                break

# Setup UI
root = tk.Tk()
root.title("Spotify Controller")

album_art_label = tk.Label(root)
album_art_label.pack()

track_name_label = tk.Label(root)
track_name_label.pack()

artist_name_label = tk.Label(root)
artist_name_label.pack()

album_name_label = tk.Label(root)
album_name_label.pack()

skip_button = ttk.Button(root, text="Skip", command=skip_track)
skip_button.pack(side=tk.LEFT)

pause_button = ttk.Button(root, text="Pause", command=pause_playback)
pause_button.pack(side=tk.LEFT)

resume_button = ttk.Button(root, text="Play", command=resume_playback)
resume_button.pack(side=tk.LEFT)

volume_up_button = ttk.Button(root, text="Volume Up", command=volume_up)
volume_up_button.pack(side=tk.LEFT)

volume_down_button = ttk.Button(root, text="Volume Down", command=volume_down)
volume_down_button.pack(side=tk.LEFT)

select_device_button = ttk.Button(root, text="Select Device", command=select_device)
select_device_button.pack(side=tk.LEFT)

update_ui()
root.mainloop()
