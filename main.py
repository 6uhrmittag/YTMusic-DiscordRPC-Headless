# uses: https://github.com/sigma67/ytmusicapi
#
# A Python Script to set the Discord Rich Presence to the currently playing song on YouTube Music using the unofficial ytmusicapi.
#
# Setup env:
# python3 -m venv venv
# source venv/bin/activate
# pip install ytmusicapi

# follow the instructions in the browser to authenticate: https://ytmusicapi.readthedocs.io/en/stable/setup/browser.html

# run script: python3 main.py

from ytmusicapi import YTMusic
import time
import json
from datetime import datetime, timedelta
from pypresence import Presence  # Import the pypresence library for Discord Rich Presence

# Initialize YTMusic with authentication
yt = YTMusic('browser.json')

# Initialize Discord Rich Presence
client_id = 'your_discord_client_id'  # Replace with your Discord application's client ID
RPC = Presence(client_id)
RPC.connect()

# Function to log the current state to a temporary file
def log_current_state(state):
    with open("current_state_log.json", "w") as log_file:
        json.dump(state, log_file, indent=4)

# Function to update Discord Rich Presence
def update_discord_presence(track):
    try:
        title = track.get("title", "Unknown Title")
        artist = track.get("artists", [{"name": "Unknown Artist"}])[0].get("name")
        duration_seconds = track.get("duration_seconds", 0)
        start_time = track.get("play_time", datetime.now()).timestamp()

        RPC.update(
            state=f"by {artist}",
            details=title,
            start=start_time,
            large_image="ytmusic_logo",  # Replace with your image key
            large_text="YouTube Music",
            small_image="play_icon",  # Replace with your image key
            small_text="Playing"
        )
        print(f"Updated Discord Rich Presence: {title} by {artist}")
    except Exception as e:
        print(f"Error updating Discord Rich Presence: {e}")

# Function to estimate the currently playing song
def estimate_current_song(previous_track, skip_first):
    try:
        history_results = yt.get_history()
        if not history_results:
            print("No history available.")
            return None

        most_recent_track = history_results[0]
        title = most_recent_track.get("title", "Unknown Title")
        duration_seconds = most_recent_track.get("duration_seconds", 0)

        # Skip output for the first song after starting the program
        if skip_first:
            print("Skipping the first track as it is most likely not playing.")
            most_recent_track["play_time"] = datetime.now()  # Set play_time to now for tracking purposes
            return most_recent_track

        # Use the system clock to estimate the most recent play
        now = datetime.now()

        if previous_track and "play_time" in previous_track:
            time_elapsed = (now - previous_track.get("play_time")).total_seconds()

            # Reset state if the song is played longer than its duration
            if time_elapsed > previous_track.get("duration_seconds", 0):
                print(f"Song {previous_track.get('title')} has exceeded its duration. Resetting state.")
                previous_track = None
            elif previous_track.get("title") == title:
                print(f"Currently Playing: {title} (elapsed {time_elapsed:.1f}/{duration_seconds} seconds)")
                return previous_track

        # Assume the song just started playing
        play_time = now - timedelta(seconds=duration_seconds)
        print(f"Currently Playing: {title} (estimated start: {play_time.strftime('%Y-%m-%d %H:%M:%S')})")

        # Log the current state
        current_state = {
            "title": title,
            "duration_seconds": duration_seconds,
            "play_time": play_time.strftime('%Y-%m-%d %H:%M:%S')
        }
        log_current_state(current_state)

        # Update the track with an estimated play time
        most_recent_track["play_time"] = play_time

        # Update Discord Rich Presence
        update_discord_presence(most_recent_track)

        return most_recent_track

    except Exception as e:
        print(f"Error fetching history: {e}")
        return None

# Main loop to periodically estimate the current song
print("Starting estimation loop...")
previous_track = None
skip_first = True
minimum_frequency = 5 * 60  # 5 minutes in seconds
buffer_time = 5  # 5 seconds buffer

while True:
    previous_track = estimate_current_song(previous_track, skip_first)
    skip_first = False  # After the first iteration, stop skipping

    # Dynamically calculate the next sleep time
    if previous_track:
        duration_seconds = previous_track.get("duration_seconds", minimum_frequency)
        elapsed_time = (datetime.now() - previous_track.get("play_time", datetime.now())).total_seconds()

        if duration_seconds < minimum_frequency:
            sleep_time = max(0, duration_seconds - elapsed_time + buffer_time)
        else:
            sleep_time = minimum_frequency
    else:
        sleep_time = minimum_frequency

    print(f"Waiting for {sleep_time} seconds before the next check...")
    time.sleep(sleep_time)

# TODO: Ensure the script handles authentication errors and prompts the user to re-authenticate if needed
# TODO: Add error handling for network issues or API rate limits