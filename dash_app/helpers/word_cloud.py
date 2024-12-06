import matplotlib.pyplot as plt
from wordcloud import WordCloud
import base64
import os
import json
from dotenv import load_dotenv
from io import BytesIO
from google.oauth2 import service_account
from google.cloud import storage

# Load Environment Variables
load_dotenv()

# Set up Google Cloud credentials
credentials_info = os.getenv("GOOGLE_AUTH")
credentials = service_account.Credentials.from_service_account_info(
    json.loads(credentials_info),
    scopes=[
        'https://www.googleapis.com/auth/devstorage.read_write',
        'https://www.googleapis.com/auth/cloud-platform',
        'https://www.googleapis.com/auth/drive'
    ]
)

# Initialize Google Cloud Storage client
storage_client = storage.Client(credentials=credentials)

def generate_word_cloud(podcast_id, bucket_name="spotify-podcast-cluster", folder="podcast_tokens"):
    """
    Generate a word cloud for a specific podcast ID from a .csv file stored in Google Cloud Storage.

    Args:
        podcast_id (str): The podcast ID to generate the word cloud for.
        bucket_name (str): The GCS bucket name where the files are stored.
        folder (str): The folder within the bucket where the .csv files are located.

    Returns:
        str: A base64-encoded string of the word cloud image.
    """
    # Path to the .csv file in GCS
    blob_name = f"{folder}/{podcast_id}.csv"
    
    # Access the bucket and blob
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)

    # Check if the file exists
    if not blob.exists():
        raise FileNotFoundError(f"The file {blob_name} does not exist in bucket {bucket_name}.")

    # Download the content of the .csv file
    csv_content = blob.download_as_text()

    # Read the tokens and their counts
    word_counts = {}
    for line in csv_content.splitlines()[1:]:  # Skip the header line
        word, count = line.strip().split(",")
        word_counts[word] = int(count)

    # Generate the word cloud
    wordcloud = WordCloud(
        width=400,
        height=400,
        background_color="#282828",
        colormap="RdYlGn"
    ).generate_from_frequencies(word_counts)

    # Save the word cloud to a BytesIO object
    buffer = BytesIO()
    plt.figure(figsize=(4, 4))
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    plt.tight_layout(pad=0)
    plt.savefig(buffer, format="png")
    buffer.seek(0)

    # Convert BytesIO to base64 string
    img_base64 = base64.b64encode(buffer.read()).decode("utf-8")
    buffer.close()

    # Return the base64-encoded string
    return f"data:image/png;base64,{img_base64}"
