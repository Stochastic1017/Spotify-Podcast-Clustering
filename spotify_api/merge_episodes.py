import os
import pandas as pd

def merge_csv_files_in_directory(directory, output_file):
    """
    Recursively traverse a directory and merge all CSV files into one large file.

    Parameters:
    - directory (str): The root directory to search for CSV files.
    - output_file (str): The path for the output CSV file.

    Returns:
    None
    """
    # List to store valid dataframes
    csv_data = []
    
    # Walk through directory and its subdirectories
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".csv"):  # Check if the file is a CSV
                file_path = os.path.join(root, file)
                print(f"Processing file: {file_path}")
                try:
                    # Read CSV into a dataframe
                    df = pd.read_csv(file_path)
                    # Check if the DataFrame is empty or all columns are NaN
                    if not df.empty and not df.isna().all(axis=None):
                        csv_data.append(df)
                    else:
                        print(f"Skipping empty or all-NaN file: {file_path}")
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")
    
    # Concatenate all valid dataframes into one
    if csv_data:
        merged_df = pd.concat(csv_data, ignore_index=True)
        merged_df[~merged_df['episode_language'].isin(['cs', 'ja', 'es-MX', 'es-ES', 'es'])].to_csv(output_file, index=False)
        print(f"All files merged into: {output_file}")
    else:
        print("No valid CSV files found.")

# Example usage
directory_path = "podcasts/"
output_csv_file = "combined_episodes.csv"
merge_csv_files_in_directory(directory_path, output_csv_file)
