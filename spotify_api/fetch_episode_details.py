
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

podcast_details = pd.read_csv("podcast_details.csv")
VALID_CATEGORIES = podcast_details['category'].unique()

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

        # Store the token and its expiry time
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


def load_podcasts_by_category(category, filepath='top_podcasts.csv'):
    """
    Load podcasts from the CSV for the specified category.
    """
    podcasts = []
    try:
        df = pd.read_csv(filepath)
        df.rename(columns={'Genre': 'category', 'Podcast': 'name', 'Image': 'img'}, inplace=True)

        if category not in VALID_CATEGORIES:
            raise ValueError(f"Invalid category: {category}. Valid categories are: {', '.join(VALID_CATEGORIES)}")

        podcasts = df[df['category'] == category].to_dict(orient='records')
    except Exception as e:
        print(f"Error loading podcasts by category: {e}")

    return podcasts

def validate_scraped_episodes(podcast_name, show_id, scraped_count, details_filepath='podcast_details.csv'):
    """
    Validate that the number of scraped episodes matches the expected total episodes from podcast_details.csv.
    """
    try:
        # Find the row for the given podcast by name and ID
        podcast_row = podcast_details[(podcast_details['name'] == podcast_name) & 
                                       (podcast_details['id'] == show_id)]
        
        if podcast_row.empty:
            print(f"Warning: Podcast '{podcast_name}' with ID '{show_id}' not found in {details_filepath}. Skipping validation.")
            return True  # Skip validation if details are missing

        # Get the total_episodes value from the CSV
        expected_count = int(podcast_row.iloc[0]['total_episodes'])

        # Compare the scraped count with the expected count
        if scraped_count != expected_count:
            print(f"Validation Failed: Podcast '{podcast_name}' has {scraped_count} episodes scraped, "
                  f"but {expected_count} episodes are listed in {details_filepath}.")
            return False
        else:
            print(f"Validation Passed: Podcast '{podcast_name}' scraped episode count matches the expected count.")
            return True

    except Exception as e:
        print(f"Error during validation for podcast '{podcast_name}': {e}")
        return False

def get_podcast_id_by_name(podcast_name):
    """
    Fetch the Spotify podcast ID by its name with comprehensive search.
    """
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header()

    search_variations = [
        podcast_name,
        podcast_name.lower(),
        podcast_name.strip(),
        re.sub(r'\s+', ' ', podcast_name),
        podcast_name.replace(':', ''),
        podcast_name.replace('-', ' ')
    ]

    for search_query in search_variations:
        params = {
            "q": search_query,
            "type": "show",
            "limit": 20  # Increased from 10 to capture more results
        }

        try:
            response = get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            
            shows = response.json().get('shows', {}).get('items', [])

            # Try multiple matching strategies
            exact_matches = [
                show for show in shows
                if show['name'].lower().strip() == search_query.lower().strip()
            ]

            if exact_matches:
                return exact_matches[0]['id']

            # If no exact match, try more lenient matching
            partial_matches = [
                show for show in shows
                if search_query.lower() in show['name'].lower()
            ]

            if partial_matches:
                return partial_matches[0]['id']

            # Fallback to first result if nothing else works
            if shows:
                return shows[0]['id']

        except Exception as e:
            print(f"Error searching for podcast {search_query}: {e}")

    print(f"No podcast found with name variations: {podcast_name}")
    return None

def get_all_episodes_from_show(show_id):
    """
    Fetch ALL episodes from a Spotify show with aggressive pagination and error handling.
    """
    global token_info
    all_episodes = []
    offset = 0
    limit = 50
    max_attempts = 5

    while True:
        url = f'https://api.spotify.com/v1/shows/{show_id}/episodes'
        headers = get_auth_header()
        params = {
            'limit': limit,
            'offset': offset
        }

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

                if not episodes_batch:
                    print(f"No more episodes to fetch. Total fetched: {len(all_episodes)}")
                    return all_episodes

                all_episodes.extend(episodes_batch)
                print(f"Fetched {len(episodes_batch)} episodes. Total so far: {len(all_episodes)}")
                offset += limit

                total_episodes = response_json.get('total', 0)
                if offset >= total_episodes:
                    print(f"Fetched all {total_episodes} episodes.")
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

def load_podcasts_from_csv(filepath='top_podcasts.csv'):
    """
    Load podcasts from CSV with error handling.
    """
    podcasts = []
    try:
        with open(filepath, mode='r', encoding='utf-8') as file:
            csv_reader = csv.reader(file)
            next(csv_reader, None)

            for row in csv_reader:
                if len(row) >= 3:
                    podcasts.append({
                        'genre': row[0],
                        'name': row[1],
                        'img': row[2]
                    })
    except Exception as e:
        print(f"Error reading podcasts CSV: {e}")

    return podcasts

def save_episodes_to_csv(episodes, show_id, podcast_name, genre='', details_filepath='podcast_details.csv'):
    """
    Save the list of episodes to a CSV file with show ID as filename.
    """

    # Validate scraped episode count against expected total episodes from the details CSV
    scraped_count = len(episodes)
    print("Validating Count:", validate_scraped_episodes(podcast_name, show_id, scraped_count, details_filepath))
        
    # Create necessary directories
    os.makedirs('shows', exist_ok=True)
    genre_folder = os.path.join('shows', sanitize_filename(genre) or 'Unknown_Genre')
    os.makedirs(genre_folder, exist_ok=True)

    # Generate filename using show ID
    filename = os.path.join(genre_folder, f"{show_id}.csv")

    # Define headers based on the episode dictionary keys
    headers = [
        'id', 'audio_preview_url', 'description', 'duration_ms', 'explicit',
        'external_urls', 'href', 'html_description', 'language', 'languages',
        'name', 'release_date', 'release_date_precision', 'type', 'uri',
        'podcast_name', 'podcast_genre', 'is_externally_hosted', 'is_playable', 'images'
    ]

    try:
        with open(filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=headers)
            writer.writeheader()

            for episode in episodes:
                try:
                    if not episode or not isinstance(episode, dict):
                        raise ValueError("Malformed episode data.")

                    # Safely extract nested fields and provide robust fallbacks
                    writer.writerow({
                        'id': episode.get('id', 'N/A'),  # Use 'N/A' to signify missing IDs
                        'audio_preview_url': episode.get('audio_preview_url', 'N/A'),
                        'description': episode.get('description', 'No description available'),
                        'duration_ms': episode.get('duration_ms', 0),  # Default to 0 if duration is missing
                        'explicit': episode.get('explicit', False),
                        'external_urls': episode.get('external_urls', {}).get('spotify', 'N/A'),
                        'href': episode.get('href', 'N/A'),
                        'html_description': episode.get('html_description', 'No HTML description'),
                        'language': episode.get('language', 'Unknown'),
                        'languages': ', '.join(episode.get('languages', [])) if isinstance(episode.get('languages'), list) else 'N/A',
                        'name': episode.get('name', 'Unnamed Episode'),
                        'release_date': episode.get('release_date', 'Unknown Date'),
                        'release_date_precision': episode.get('release_date_precision', 'Unknown'),
                        'type': episode.get('type', 'Unknown'),
                        'uri': episode.get('uri', 'N/A'),
                        'podcast_name': podcast_name or 'Unknown Podcast',
                        'podcast_genre': genre or 'Unknown Genre',
                        'is_externally_hosted': episode.get('is_externally_hosted', None),
                        'is_playable': episode.get('is_playable', None),
                        'images': '; '.join([img.get('url', 'N/A') for img in episode.get('images', [])]) 
                                if isinstance(episode.get('images'), list) else 'N/A'
                    })
        
                except Exception as row_error:
                    print(f"Error writing episode row for podcast '{podcast_name}': {row_error}")
                    # Log detailed information for troubleshooting
                    with open("problematic_episodes.log", "a") as log_file:
                        log_file.write(f"Podcast: {podcast_name}, Error: {row_error}, Episode: {episode}\n")
                    
        print(f"Saved {len(episodes)} episodes for {podcast_name} to {filename}")

    except Exception as e:
        print(f"Error saving CSV for {podcast_name}: {e}")

def sanitize_filename(name):
    """
    Sanitize the podcast name to make it a valid filename.
    """
    return re.sub(r'[^\w\s-]', '', str(name)).replace(" ", "_")

def process_podcast(podcast):
    """
    Process a single podcast with enhanced error handling.
    """
    name = podcast.get('name')
    genre = podcast.get('category')

    try:
        show_id = get_podcast_id_by_name(name)
        print(f"Currently at: {name} <-> url: https://open.spotify.com/show/{show_id}")

        if not show_id:
            with open("unresolved_podcasts.log", "a") as log_file:
                log_file.write(f"Could not resolve podcast: {name}\n")
            return f"No show ID found for {name}"

        episodes = get_all_episodes_from_show(show_id)
        if not episodes:
            with open("no_episodes_podcasts.log", "a") as log_file:
                log_file.write(f"No episodes found for: {name} (Show ID: {show_id})\n")
            return f"No episodes found for {name}"

        save_episodes_to_csv(episodes, show_id, name, genre)
        return f"Processed {name} - {len(episodes)} episodes"

    except Exception as e:
        with open("podcast_processing_errors.log", "a") as log_file:
            log_file.write(f"Error processing {name}: {e}\n")
        return f"Error processing {name}: {e}"

def main():
    """
    Main function to scrape episodes from podcasts in a specific category.
    """
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <category1> <category2> ...")
        print(f"Valid categories: {', '.join(VALID_CATEGORIES)}")
        return

    categories = sys.argv[1:]

    for category in categories:
        if category not in VALID_CATEGORIES:
            print(f"Invalid category: {category}. Skipping. Valid categories are: {', '.join(VALID_CATEGORIES)}")
            continue

        print(f"Processing category: {category}")
        
        token = get_token()
        if not token:
            print("Failed to obtain Spotify API token. Exiting.")
            return

        podcasts = load_podcasts_by_category(category)
        if not podcasts:
            print(f"No podcasts found for category: {category}")
            continue

        for log_file in ["unresolved_podcasts.log", 
                         "no_episodes_podcasts.log", 
                         "podcast_processing_errors.log"]:
            open(log_file, 'w').close()

        problem_podcasts = []

        for podcast in tqdm(podcasts, desc=f"Processing Podcasts in {category}"):
            result = process_podcast(podcast)
            print(result)
            if "Error" in result or "No show ID" in result or "No episodes" in result:
                problem_podcasts.append(podcast)
            time.sleep(3)

        print(f"\nProblematic Podcasts for category {category}:")
        for prob_podcast in problem_podcasts:
            print(f"- {prob_podcast.get('name', 'Unknown')}")

if __name__ == "__main__":
    main()
