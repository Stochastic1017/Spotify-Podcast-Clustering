# Clustering Spotify Podcasts with NLP-Driven Insights

## Introduction

Spotify has already developed several music-specific metrics/derived features about a particular track/music, specifically: (a) acousticness, (b) danceability, (c) energy, (d) instrumentalness, (e) speechiness, and (f) valence.
All these metrics are in the range of [0,1] and can be used to cluster users based on their musical taste. This project is meant to construct similar informative metrics for Spotify’s podcast data, and create a novel recommendation system based on these metrics.

## Data Collection using Spotify API

Using selenium and Spotify API:

* *[`fetch_top_podcast.py`](https://github.com/Stochastic1017/Spotify-Podcast-Clustering/blob/main/spotify_api/fetch_top_podcast.py):* scrape all top 50 podcasts from  [here](https://podcastcharts.byspotify.com/) for each genre.
* *[`fetch_podcast_details.py`](https://github.com/Stochastic1017/Spotify-Podcast-Clustering/blob/main/spotify_api/fetch_podcast_details.py):* retrieve metadata, filtered for english podcasts, resulting in 818 podcasts.
* *[`fetch_episode_details.py`](https://github.com/Stochastic1017/Spotify-Podcast-Clustering/blob/main/spotify_api/fetch_episode_details.py):* scrape details for all episodes, giving us a total of 284,481 episodes.

## Description cleanup and tokenization

The python library `nltk` (natural language toolkit) is used to clean and tokenize the episode descriptions. In summary, the following cleaning is done using [`clean\_description.py`](https://github.com/Stochastic1017/Spotify-Podcast-Clustering/blob/main/tokenization/clean_description.py):

* *Text Normalization:* accent removal, lowercasing, whitespace normalization.
* *Sentence-Level Cleaning:* contraction expansion, URL removal, promotional density check.
* *Token-Level Cleaning:* lemmatization, stopword removal, promotional keyword removal, character validation, length check, dictionary validation, special character removal.

## Computing metrics

The [`compute_metrics.py`](https://github.com/Stochastic1017/Spotify-Podcast-Clustering/blob/main/models/compute_metrics.py) script computes three metrics:

### Normalized Total Feature Similarity (NTFS)

The NTFS metric measures the cosine similarity between two frequency vectors and is defined as:

```math
\text{NTFS}(\mathbf{x},\mathbf{y}) = \frac{\langle \mathbf{x}, \mathbf{y}\rangle}{\|\mathbf{x}\|_{2}\;\|\mathbf{y}\|_{2}} \in \mathbb{R}_{[0,1]}, \quad \longrightarrow \text{directional similarity between two podcasts}
```

### Jaccard Token Similarity (JTS)

Compute JTS metric signifying proportion of overlapping tokens.

```math
\text{JTS}(\mathbf{x},\mathbf{y}) = \frac{\sum \text{min}(x_i, y_i)}{\sum \text{max}(x_i, y_i)} \in \mathbb{R}_{[0,1]}, \quad \longrightarrow \text{shared content coverage between two podcasts}
```

### Weighted Token Diversity Similarity (WTDS)

Uses L1-normalized frequency vectors that emphasizing token diversity.

```math
\text{WTDS}(\mathbf{x},\mathbf{y}) = \sum_{i=1}^{n} \sqrt{ \frac{x_i}{\|\mathbf{x}\|_{1}} \cdot \frac{y_i}{\|\mathbf{y}\|_{1}} } \in \mathbb{R}_{[0,1]}, \quad \longrightarrow \text{shared content diversity between two podcasts}
```

Here is the python implementation for computing the above metrics:

```python
# Helper Functions
def get_global_vocabulary(podcast_ids, folder="podcast_tokens"):
    global_vocab = set()
    n = len(podcast_ids)
    for idx, podcast_id in enumerate(podcast_ids):
        print(f"processing: {podcast_id}. At {idx} out of {n}")
        file_path = os.path.join(folder, f"{podcast_id}.csv")
        if os.path.exists(file_path):
            word_counts = pd.read_csv(file_path)
            global_vocab.update(word_counts["Word"])
    return list(global_vocab)

def get_token_frequency_vectors(podcast_ids, global_vocab, folder="podcast_tokens"):
    vocab_index = {word: idx for idx, word in enumerate(global_vocab)}
    vectors = []
    n = len(podcast_ids)
    for idx, podcast_id in enumerate(podcast_ids):
        print(f"processing: {podcast_id}. At {idx} out of {n}")
        file_path = os.path.join(folder, f"{podcast_id}.csv")
        if os.path.exists(file_path):
            word_counts = pd.read_csv(file_path)
            freq_vector = np.zeros(len(global_vocab))
            for _, row in word_counts.iterrows():
                if row["Word"] in vocab_index:
                    freq_vector[vocab_index[row["Word"]]] = row["Count"]
            vectors.append(freq_vector)
    return np.array(vectors)

def compute_similarity_matrices(freq_vectors):
    print("Computing NTFS ...")
    ntfs_matrix = cosine_similarity(normalize(freq_vectors, norm='l2'))
    print("Computing JTS ...")
    jts_matrix = np.array([
        [np.sum(np.minimum(freq_vectors[i], freq_vectors[j])) / np.sum(np.maximum(freq_vectors[i], freq_vectors[j])) if np.sum(np.maximum(freq_vectors[i], freq_vectors[j])) > 0 else 0
         for j in range(len(freq_vectors))]
        for i in range(len(freq_vectors))
    ])
    print("Computing WTDS ...")
    wtds_matrix = np.array([
        [np.sum(np.sqrt(normalize(freq_vectors[i:i+1], norm='l1') * normalize(freq_vectors[j:j+1], norm='l1'))) 
         for j in range(len(freq_vectors))]
        for i in range(len(freq_vectors))
    ])
    return ntfs_matrix, jts_matrix, wtds_matrix
```

### Recommendation System

Suppose an arbitrary podcast $k$ is chosen, for which an $n$-recommendation needs to be generated from a list of $T$ podcasts. Consider a matrix of the following form:


