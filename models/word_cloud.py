import matplotlib.pyplot as plt
from wordcloud import WordCloud
import os
import glob
from io import BytesIO
import matplotlib

matplotlib.use('Agg')  # Use a non-GUI backend

def generate_word_cloud_local(podcast_id, input_folder="podcast_tokens", output_folder="wordclouds"):
    """
    Generate a word cloud for a specific podcast ID from a .csv file stored locally.

    Args:
        podcast_id (str): The podcast ID to generate the word cloud for.
        input_folder (str): The local folder where the .csv files are located.
        output_folder (str): The folder where the word cloud images will be saved.

    Returns:
        str: The path to the saved word cloud image file.
    """
    # Path to the .csv file
    file_path = os.path.join(input_folder, f"{podcast_id}.csv")

    # Check if the file exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file {file_path} does not exist in folder {input_folder}.")

    # Read the tokens and their counts
    word_counts = {}
    with open(file_path, "r") as file:
        lines = file.readlines()
        if len(lines) <= 1:  # No data apart from the header
            word_counts = None
        else:
            for line in lines[1:]:  # Skip the header line
                word, count = line.strip().split(",")
                word_counts[word] = int(count)

    # Generate the word cloud
    wordcloud = WordCloud(
        width=400,
        height=400,
        background_color="#282828",
        colormap="RdYlGn"
    )

    if word_counts:
        wordcloud = wordcloud.generate_from_frequencies(word_counts)

    # Ensure the output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # Save the word cloud as an image file
    output_path = os.path.join(output_folder, f"{podcast_id}.png")
    plt.figure(figsize=(4, 4))
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    plt.tight_layout(pad=0)
    plt.savefig(output_path, format="png")
    plt.close()

    # Return the path to the saved image file
    return output_path

def generate_word_clouds_for_all(input_folder="podcast_tokens", output_folder="wordclouds"):
    """
    Generate word clouds for all podcast IDs in the specified input folder and save them in the output folder.

    Args:
        input_folder (str): The local folder where the .csv files are located.
        output_folder (str): The folder where the word cloud images will be saved.
    """
    # Find all .csv files in the folder
    csv_files = glob.glob(os.path.join(input_folder, "*.csv"))
    
    if not csv_files:
        print(f"No .csv files found in folder {input_folder}.")
        return

    # Process each .csv file
    for csv_file in csv_files:
        # Extract podcast_id from the file name
        podcast_id = os.path.splitext(os.path.basename(csv_file))[0]
        
        try:
            # Generate the word cloud
            output_path = generate_word_cloud_local(podcast_id, input_folder=input_folder, output_folder=output_folder)
            print(f"Word cloud saved as {output_path}")
        except Exception as e:
            print(f"Error generating word cloud for {podcast_id}: {e}")

# Example usage
generate_word_clouds_for_all(input_folder="podcast_tokens", output_folder="wordclouds")
