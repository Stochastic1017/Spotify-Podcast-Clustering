
import pandas as pd
import numpy as np
import os
import time
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import normalize

start = time.time()

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

# Main Execution
print("Loading podcast metadata...")
podcast_metadata = pd.read_csv("https://raw.githubusercontent.com/Stochastic1017/Spotify-Podcast-Clustering/refs/heads/main/data/cleaned_podcast_details_english_colors.csv")
podcast_ids = podcast_metadata["podcast_id"].tolist()

print("Generating global vocabulary and frequency vectors...")
global_vocab = get_global_vocabulary(podcast_ids)
freq_vectors = get_token_frequency_vectors(podcast_ids, global_vocab)

print("Computing similarity matrices...")
ntfs_matrix, jts_matrix, wtds_matrix = compute_similarity_matrices(freq_vectors)

# Save the matrices to .npy files
try:
    with open('ntfs.npy', 'wb') as ntfs:
        np.save(ntfs, ntfs_matrix)

    with open('jts.npy', 'wb') as jts:
        np.save(jts, jts_matrix)

    with open('wtds.npy', 'wb') as wtds:
        np.save(wtds, wtds_matrix)

    print("Matrices saved successfully.")
except Exception as e:
    print(f"Error saving matrices: {e}")
    exit(1)

print("Time Taken:", (time.time() - start) / 60, "minutes.")
