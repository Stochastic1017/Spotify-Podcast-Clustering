
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import base64
from io import BytesIO

def generate_word_cloud(podcast_id, tokens_dir="podcast_tokens"):

    # Path to the tokens file for the given podcast ID
    tokens_file = f"{tokens_dir}/{podcast_id}.csv"
    
        # Read the tokens and their counts
    word_counts = {}
    with open(tokens_file, "r") as f:
        next(f)
        for line in f:
            word, count = line.strip().split(",")
            word_counts[word] = int(count)
    
    # Generate the word cloud
    wordcloud = WordCloud(width=400, 
                          height=400, 
                          background_color="#282828", 
                          colormap="RdYlGn").generate_from_frequencies(word_counts)
    
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
