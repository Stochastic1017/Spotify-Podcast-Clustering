
import os
import pandas as pd

# Paths
podcast_tokens_folder = "podcast_tokens/"
podcast_details_file = "data/podcast_details.csv"
output_file = "data/cleaned_podcast_details.csv"

# Step 1: Get the list of podcast IDs from the podcast_tokens folder
podcast_ids = [
    os.path.splitext(filename)[0] for filename in os.listdir(podcast_tokens_folder) if filename.endswith(".csv")
]

# Step 2: Load the podcast_details.csv file
podcast_details = pd.read_csv(podcast_details_file)

# Step 3: Filter the podcast_details dataframe to include only rows with IDs in podcast_ids
cleaned_podcast_details = podcast_details[podcast_details["podcast_id"].isin(podcast_ids)]

# Step 4: Save the cleaned dataframe to a new CSV file
cleaned_podcast_details.to_csv(output_file, index=False)

print(f"Cleaned podcast details saved to {output_file}")
