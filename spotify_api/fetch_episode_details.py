import base64
import os
import sys
import time
import csv
import re
import pandas as pd
from dotenv import load_dotenv
from requests import post, get
from tqdm import tqdm

# Load environment variables
load_dotenv(override=True)
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

token_info = {
    "access_token": None,
    "expires_at": 0
}

# Load input CSV
podcast_details = pd.read_csv("podcast_details_english_colors.csv")

def get_token():
    """Obtain Spotify API access token."""
    global token_info
    auth_string = f"{CLIENT_ID}:{CLIENT_SECRET}"
    auth_bytes = auth_string.encode('utf-8')
    auth_base64 = str(base64.b64encode(auth_bytes), 'utf-8')

    url = 'https://accounts.spotify.com/api/token'
    headers = {
        "Authorization": f"Basic {auth_base64}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}

    try:
        result = post(url, headers=headers, data=data)
        result.raise_for_status()
        json_result = result.json()

        token_info['access_token'] = json_result['access_token']
        token_info['expires_at'] = time.time() + json_result['expires_in']
        return token_info['access_token']
    except Exception as e:
        print(f"Error obtaining token: {e}")
        return None

def get_auth_header():
    """Create authorization header with dynamic token refreshing."""
    global token_info
    if not token_info['access_token'] or time.time() > token_info['expires_at'] - 300:
        token_info['access_token'] = get_token()
    return {"Authorization": f"Bearer {token_info['access_token']}"}

def get_all_episodes_from_show(show_id):
    """
    Fetch all episodes from a Spotify show with detailed monitoring of batch sizes.
    """
    all_episodes = []
    offset = 0
    limit = 50
    max_attempts = 5

    while True:
        url = f'https://api.spotify.com/v1/shows/{show_id}/episodes'
        headers = get_auth_header()
        params = {'limit': limit, 'offset': offset}

        attempts = 0
        while attempts < max_attempts:
            try:
                response = get(url, headers=headers, params=params)

                if response.status_code == 401:  # Unauthorized (token expired)
                    print("Token expired. Refreshing token...")
                    token_info['access_token'] = get_token()
                    headers = get_auth_header()
                    continue

                if response.status_code == 429:  # Rate limit
                    retry_after = max(int(response.headers.get("Retry-After", 5)), 600)
                    print(f"Rate limit exceeded. Retrying after {retry_after} seconds...")
                    time.sleep(retry_after)
                    continue

                response.raise_for_status()
                response_json = response.json()
                episodes_batch = response_json.get('items', [])

                batch_size = len(episodes_batch)
                print(f"Fetched batch of {batch_size} episodes. Offset: {offset}")

                all_episodes.extend(episodes_batch)
                offset += limit

                if not episodes_batch or offset >= response_json.get('total', 0):
                    print(f"Finished fetching episodes. Total episodes fetched: {len(all_episodes)}")
                    return all_episodes

                time.sleep(3)
                break

            except Exception as e:
                print(f"Error fetching episodes for show ID {show_id} (Attempt {attempts+1}): {e}")
                attempts += 1
                time.sleep(3)

        if attempts == max_attempts:
            print(f"Failed to fetch episodes for show ID {show_id} after {max_attempts} attempts.")
            break

    return all_episodes

def save_episodes_to_csv(episodes, podcast_id, podcast_name, genre, dominant_color):
    """
    Save the list of episodes to a CSV file with show ID as filename.
    """
    os.makedirs('podcasts/', exist_ok=True)
    genre_folder = os.path.join('podcasts', sanitize_filename(genre) or 'Unknown_Genre')
    os.makedirs(genre_folder, exist_ok=True)

    filename = os.path.join(genre_folder, f"{sanitize_filename(podcast_name)}.csv")
    log_filename = "problematic_episodes.log"

    headers = [
        'episode_id', 'episode_name', 'episode_description', 'episode_duration_ms',
        'episode_explicit', 'episode_release_date', 'episode_language', 'podcast_id',
        'podcast_name', 'podcast_genre', 'podcast_dominant_color'
    ]

    try:
        with open(filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=headers)
            writer.writeheader()

            for episode in episodes:
                if not episode or not isinstance(episode, dict):
                    with open(log_filename, "a") as log_file:
                        log_file.write(f"Malformed episode data: {episode}\n")
                    continue

                try:
                    writer.writerow({
                        'episode_id': episode.get('id', 'N/A'),
                        'episode_name': episode.get('name', 'Unnamed Episode'),
                        'episode_description': episode.get('description', 'No description available'),
                        'episode_duration_ms': episode.get('duration_ms', 0),
                        'episode_explicit': episode.get('explicit', False),
                        'episode_release_date': episode.get('release_date', 'Unknown Date'),
                        'episode_language': episode.get('language', 'Unknown'),
                        'podcast_id': podcast_id,
                        'podcast_name': podcast_name,
                        'podcast_genre': genre,
                        'podcast_dominant_color': dominant_color
                    })

                except Exception as row_error:
                    print(f"Error writing episode row: {row_error}")
                    with open(log_filename, "a") as log_file:
                        log_file.write(f"Error writing row: {row_error}, Episode: {episode}\n")

        print(f"Saved {len(episodes)} episodes for {podcast_name} to {filename}")

    except Exception as e:
        print(f"Error saving CSV for {podcast_name}: {e}")

def sanitize_filename(name):
    """Sanitize a string to make it a valid filename."""
    return re.sub(r'[^\w\s-]', '', str(name)).replace(" ", "_")

def process_podcast(podcast):
    """
    Process a single podcast, fetching its episodes and saving them.
    """
    podcast_id = podcast['podcast_id']
    podcast_name = podcast['podcast_name']
    genre = podcast['podcast_genre']
    dominant_color = podcast['podcast_dominant_color']

    try:
        episodes = get_all_episodes_from_show(podcast_id)
        if not episodes:
            print(f"No episodes found for {podcast_name}")
            return

        save_episodes_to_csv(episodes, podcast_id, podcast_name, genre, dominant_color)
    except Exception as e:
        print(f"Error processing {podcast_name}: {e}")

def main():
    """
    Main function to process podcasts by genre.
    """
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} - choose one from {podcast_details['podcast_genre'].unique()} ...")
        return

    genres = sys.argv[1:]

    for genre in genres:
        podcasts = podcast_details[podcast_details['podcast_genre'] == genre].to_dict(orient='records')

        if not podcasts:
            print(f"No podcasts found for genre: {genre}")
            continue

        for podcast in tqdm(podcasts, desc=f"Processing Podcasts in {genre}"):
            process_podcast(podcast)
            time.sleep(3)

if __name__ == "__main__":
    main()
