
import os
import csv
import time
import spotipy
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd

class SpotifyPodcastFetcher:

    def __init__(self, client_id, client_secret):
        """
        Initialize Spotify client with credentials
        
        :param client_id: Spotify Developer App Client ID
        :param client_secret: Spotify Developer App Client Secret
        """
        self.client_credentials_manager = SpotifyClientCredentials(
            client_id=client_id, 
            client_secret=client_secret
        )
        self.sp = spotipy.Spotify(client_credentials_manager=self.client_credentials_manager)
    
    def search_podcast(self, podcast_name):
        """
        Search for a podcast and return its Spotify show details.
        
        :param podcast_name: Name of the podcast to search
        :return: Dictionary of podcast details or None if not found
        """
        try:
            # Search for the podcast show
            results = self.sp.search(q=podcast_name, type='show', limit=1)
            
            if results['shows']['items']:
                show = results['shows']['items'][0]
                return {
                    'name': show['name'],
                    'id': show['id'],
                    'description': show.get('description', ''),
                    'html_description': show.get('html_description', ''),
                    'publisher': show.get('publisher', ''),
                    'languages': show.get('languages', []),
                    'media_type': show.get('media_type', ''),
                    'total_episodes': show.get('total_episodes', 0),
                    'available_markets': ','.join(show.get('available_markets', [])),
                    'is_externally_hosted': show.get('is_externally_hosted', False),
                    'explicit': show.get('explicit', False),
                    'external_url': show['external_urls'].get('spotify', ''),
                    'image_url': show['images'][0]['url'] if show['images'] else '',
                    'uri': show.get('uri', ''),
                    'href': show.get('href', ''),
                }
            return None
        
        except Exception as e:
            print(f"Error searching for podcast {podcast_name}: {e}")
            return None
    
    def fetch_podcasts_from_csv(self, input_csv, output_csv):
        """
        Fetch podcast details from a CSV and save results to another CSV

        :param input_csv: Path to input CSV with podcast names
        :param output_csv: Path to output CSV with podcast details
        """
        # Read the input CSV and infer headers
        df = pd.read_csv(input_csv)
        df.rename(columns={
                            'Genre': 'category',
                            'Podcast': 'podcast_name',
                            'Image': 'image_url'
                        }, inplace=True)
        print(df)
        
        # Validate required columns
        required_columns = {'category', 'podcast_name', 'image_url'}
        if not required_columns.issubset(df.columns):
            raise ValueError(f"Input CSV must contain the columns: {', '.join(required_columns)}")
        
        length_df = len(df)

        # List to store podcast details
        podcast_details = []
        
        # Iterate through podcasts with rate limiting and error handling
        for index, row in df.iterrows():
            try:
                print(f"Searching for podcast: {row['podcast_name']}. {index + 1} out of {length_df}")
                podcast_info = self.search_podcast(row['podcast_name'])
                
                if podcast_info:
                    # Merge original row data with fetched podcast info
                    podcast_info['category'] = row['category']
                    podcast_info['original_image_url'] = row['image_url']
                    podcast_details.append(podcast_info)
                
                # Rate limiting to avoid hitting API limits
                time.sleep(0.2)  # 5 requests per second
            
            except Exception as e:
                print(f"Error processing {row['podcast_name']}: {e}")
        
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
    INPUT_CSV = 'top_podcasts.csv'
    OUTPUT_CSV = 'podcast_details.csv'
    
    # Create fetcher instance
    fetcher = SpotifyPodcastFetcher(CLIENT_ID, CLIENT_SECRET)
    
    # Fetch and save podcast details
    fetcher.fetch_podcasts_from_csv(INPUT_CSV, OUTPUT_CSV)

if __name__ == "__main__":
    main()