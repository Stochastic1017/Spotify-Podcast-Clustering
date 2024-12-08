import os
import time
import spotipy
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd

class SpotifyPodcastFetcher:

    def __init__(self, client_id, client_secret):
        """
        Initialize Spotify client with credentials.
        
        :param client_id: Spotify Developer App Client ID
        :param client_secret: Spotify Developer App Client Secret
        """
        self.client_credentials_manager = SpotifyClientCredentials(
            client_id=client_id, 
            client_secret=client_secret
        )
        self.sp = spotipy.Spotify(client_credentials_manager=self.client_credentials_manager)
    
    def fetch_podcast_details(self, podcast_id):
        """
        Fetch detailed podcast information using podcast ID, including a clickable podcast URL.
        
        :param podcast_id: Spotify podcast ID
        :return: Dictionary of podcast details or None if not found
        """
        try:
            # Fetch podcast details using ID
            show = self.sp.show(podcast_id)
            return {
                'podcast_id': show['id'],
                'podcast_name': show['name'],
                'podcast_description': show.get('description', ''),
                'podcast_publisher': show.get('publisher', ''),
                'podcast_languages': show.get('languages', []),
                'podcast_total_episodes': show.get('total_episodes', 0),
                'podcast_explicit': show.get('explicit', False),
                'podcast_image_url': show['images'][0]['url'] if show['images'] else '',
                'podcast_url': show['external_urls']['spotify'],  
            }
        except Exception as e:
            print(f"Error fetching details for podcast ID {podcast_id}: {e}")
            return None
    
    def fetch_podcasts_from_csv(self, input_csv, output_csv):
        """
        Fetch podcast details from a CSV and save results to another CSV.

        :param input_csv: Path to input CSV with podcast IDs
        :param output_csv: Path to output CSV with podcast details
        """
        # Read the input CSV
        df = pd.read_csv(input_csv)

        # Validate required column
        if 'podcast_id' not in df.columns:
            raise ValueError("Input CSV must contain the column 'podcast_id'")
        
        length_df = len(df)

        # List to store podcast details
        podcast_details = []
        
        # Iterate through podcasts with rate limiting and error handling
        for index, row in df.iterrows():
            try:
                print(f"Fetching details for podcast ID: {row['podcast_id']}. {index + 1} out of {length_df}")
                podcast_info = self.fetch_podcast_details(row['podcast_id'])
                
                if podcast_info:
                    # Merge original row data with fetched podcast info
                    podcast_info['genre'] = row['podcast_genre']
                    podcast_details.append(podcast_info)
                
                # Rate limiting to avoid hitting API limits
                time.sleep(0.2)  # 5 requests per second
            
            except Exception as e:
                print(f"Error processing podcast ID {row['podcast_id']}: {e}")
        
        # Convert to DataFrame and save
        results_df = pd.DataFrame(podcast_details)
        results_df.to_csv(output_csv, index=False)
        
        print(f"Saved {len(results_df)} podcast details to {output_csv}")

def main():
    # Load environment variables
    load_dotenv(override=True)
    CLIENT_ID = os.getenv("CLIENT_ID")
    CLIENT_SECRET = os.getenv("CLIENT_SECRET")
    
    # Paths for input and output CSVs
    INPUT_CSV = 'top_podcasts_all_genre.csv'
    OUTPUT_CSV = 'podcast_details.csv'
    
    # Create fetcher instance
    fetcher = SpotifyPodcastFetcher(CLIENT_ID, CLIENT_SECRET)
    
    # Fetch and save podcast details
    fetcher.fetch_podcasts_from_csv(INPUT_CSV, OUTPUT_CSV)

if __name__ == "__main__":
    main()
