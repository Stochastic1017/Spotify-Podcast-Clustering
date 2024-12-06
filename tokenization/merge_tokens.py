
import os
import pandas as pd

# Define the parent directory and the podcast_tokens directory
parent_directory = os.path.dirname(os.path.abspath(__file__))
podcast_tokens_directory = os.path.join(parent_directory, "../podcast_tokens/")

# Initialize an empty list to store DataFrames
dfs = []

# Iterate through each file in the podcast_tokens directory
for filename in os.listdir(podcast_tokens_directory):
    if filename.endswith(".csv"):
        file_path = os.path.join(podcast_tokens_directory, filename)
        # Extract the podcast_id from the filename
        podcast_id = filename.replace(".csv", "")
        # Read the CSV file
        df = pd.read_csv(file_path)
        # Add a new column for podcast_id
        df['podcast_id'] = podcast_id
        # Append the DataFrame to the list
        dfs.append(df)

# Concatenate all DataFrames
merged_df = pd.concat(dfs, ignore_index=True)

# Save the merged DataFrame to a new CSV file
output_file = os.path.join(parent_directory, "merged_podcast_tokens.csv")
merged_df.to_csv(output_file, index=False)

print(f"Merged file saved to: {output_file}")
