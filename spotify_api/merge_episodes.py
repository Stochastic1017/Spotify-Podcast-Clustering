import os
import pandas as pd

def merge_all_csv_in_directory(base_directory):
    """
    Recursively merges all CSV files in a directory and its subdirectories into a single DataFrame.
    
    Parameters:
        base_directory (str): The root directory to start the search.
        
    Returns:
        pd.DataFrame: Merged DataFrame containing all CSV data from the directory.
    """
    all_csv_files = []
    
    # Walk through the directory and subdirectories to find CSV files
    for root, _, files in os.walk(base_directory):
        for file in files:
            if file.endswith('.csv'):
                all_csv_files.append(os.path.join(root, file))
    
    # Merge all CSV files
    merged_data = pd.DataFrame()
    for csv_file in all_csv_files:
        try:
            print(f"Reading {csv_file}...")
            data = pd.read_csv(csv_file)
            merged_data = pd.concat([merged_data, data], ignore_index=True)
        except Exception as e:
            print(f"Error reading {csv_file}: {e}")
    
    return merged_data

def combine_podcast_data(top_podcasts_file, podcast_details_file, base_directory, output_file):
    """
    Combines top podcasts, podcast details, and episode information into one file.
    
    Parameters:
        top_podcasts_file (str): Path to the top_podcasts.csv file.
        podcast_details_file (str): Path to the podcast_details.csv file.
        base_directory (str): Directory containing genre-wise episode details.
        output_file (str): Path to save the combined file.
    """
    try:
        # Load top_podcasts.csv
        print("Loading top_podcasts.csv...")
        top_podcasts = pd.read_csv(top_podcasts_file)
        
        # Load podcast_details.csv
        print("Loading podcast_details.csv...")
        podcast_details = pd.read_csv(podcast_details_file)
        
        # Normalize columns for consistent matching
        top_podcasts["Podcast"] = top_podcasts["Podcast"].str.strip().str.lower()
        podcast_details["name"] = podcast_details["name"].str.strip().str.lower()
        
        # Merge top_podcasts and podcast_details on matching columns
        print("Merging top_podcasts with podcast_details...")
        merged_podcasts = pd.merge(
            top_podcasts, podcast_details,
            left_on="Podcast", right_on="name",
            how="left"
        )
        
        # Load and merge all episode-level data
        print("Merging episode data from genre directories...")
        episodes_data = merge_all_csv_in_directory(base_directory)
        
        # Merge episode data with the combined podcast data
        print("Combining podcast and episode data...")
        combined_data = pd.merge(
            episodes_data,
            merged_podcasts,
            left_on="podcast_name",
            right_on="Podcast",
            how="left"
        )
        
        # Save the final combined data to the output file
        print(f"Saving combined data to {output_file}...")
        combined_data.to_csv(output_file, index=False)
        print(f"Successfully saved combined data to {output_file}")
    
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    # Update these paths accordingly
    TOP_PODCASTS_FILE = "top_podcasts.csv"
    PODCAST_DETAILS_FILE = "podcast_details.csv"
    BASE_DIRECTORY = "podcasts/"  # Genre-based directories
    OUTPUT_FILE = "combined_podcast_data.csv"
    
    combine_podcast_data(TOP_PODCASTS_FILE, PODCAST_DETAILS_FILE, BASE_DIRECTORY, OUTPUT_FILE)
