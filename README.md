# Clustering Spotify Podcasts with NLP-Driven Insights

## Web-App Link

The web-app link to interact with the spotify recommendation system can be found here: https://spotify-podcast-clustering.onrender.com

*Note: This service is currently suspended.*

The intro animation is taken from: https://www.youtube.com/watch?v=cB8JW-uLuC4. 

If plots or tables don't fit properly, press Ctrl - or Ctrl + to adjust the zoom level until the layout looks satisfactory.

Here is a short video to showcase the web-app:

https://github.com/user-attachments/assets/28672852-8fa0-4f2c-95a7-a28619bbca73

## Introduction

Spotify has already developed several music-specific metrics/derived features about a particular track/music, specifically: (a) acousticness, (b) danceability, (c) energy, (d) instrumentalness, (e) speechiness, and (f) valence.
All these metrics are in the range of [0,1] and can be used to cluster users based on their musical taste. This project is meant to construct similar informative metrics for Spotify’s podcast data, and create a novel recommendation system based on these metrics.

## Data Collection using Spotify API

Using selenium and Spotify API:

* *[`fetch_top_podcast.py`](https://github.com/Stochastic1017/Spotify-Podcast-Clustering/blob/main/spotify_api/fetch_top_podcast.py):* scrape all top 50 podcasts from  [here](https://podcastcharts.byspotify.com/) for each genre.
* *[`fetch_podcast_details.py`](https://github.com/Stochastic1017/Spotify-Podcast-Clustering/blob/main/spotify_api/fetch_podcast_details.py):* retrieve metadata, filtered for english podcasts, resulting in 818 podcasts.
* *[`fetch_episode_details.py`](https://github.com/Stochastic1017/Spotify-Podcast-Clustering/blob/main/spotify_api/fetch_episode_details.py):* scrape details for all episodes, giving us a total of 284,481 episodes.

## Description cleanup and tokenization

The python library `nltk` (natural language toolkit) is used to clean and tokenize the episode descriptions. In summary, the following cleaning is done using [`clean_description.py`](https://github.com/Stochastic1017/Spotify-Podcast-Clustering/blob/main/tokenization/clean_description.py):

* *Text Normalization:* accent removal, lowercasing, whitespace normalization.
* *Sentence-Level Cleaning:* contraction expansion, URL removal, promotional density check.
* *Token-Level Cleaning:* lemmatization, stopword removal, promotional keyword removal, character validation, length check, dictionary validation, special character removal.

## Computing metrics

The [`compute_metrics.py`](https://github.com/Stochastic1017/Spotify-Podcast-Clustering/blob/main/models/compute_metrics.py) script computes three metrics:

### Normalized Total Feature Similarity (NTFS)

The NTFS metric measures the cosine similarity between two frequency vectors and is defined as:

```math
\text{NTFS}(\mathbf{x},\mathbf{y}) = \frac{\langle \mathbf{x}, \mathbf{y}\rangle}{\|\mathbf{x}\|_{2}\;\|\mathbf{y}\|_{2}} \in \mathbb{R}_{[0,1]}, \quad \longrightarrow \text{higher implies more directional similarity}
```

Strengths: Robust for sparse vectors. Weakness: Assumes all tokens equally important.

### Jaccard Token Similarity (JTS)

Compute JTS metric signifying proportion of overlapping tokens.

```math
\text{JTS}(\mathbf{x},\mathbf{y}) = \frac{\sum \text{min}(x_i, y_i)}{\sum \text{max}(x_i, y_i)} \in \mathbb{R}_{[0,1]}, \quad \longrightarrow \text{higher implies more token overlap}
```

Strengths: Simple  and interpretable measure of overlap. Weakness: Sensitive to scaling.

### Weighted Token Diversity Similarity (WTDS)

Uses L1-normalized frequency vectors that emphasizing token diversity.

```math
\text{WTDS}(\mathbf{x},\mathbf{y}) = \sum_{i=1}^{n} \sqrt{ \frac{x_i}{\|\mathbf{x}\|_{1}} \cdot \frac{y_i}{\|\mathbf{y}\|_{1}} } \in \mathbb{R}_{[0,1]}, \quad \longrightarrow \text{higher implies more shared diversity}
```

Strength: Highlights diversity. Weakness: Assumes uniform importance across tokens.

The resulting combined matrix (where each element in $\mathbb{R}^3_{[0,1]}$) is as follows:

```math
\begin{array}{cccccc}
    & \text{podcast}_1 & \dots & \text{podcast}_k & \dots & \text{podcast}_T \\
    \text{podcast}_1 & (1, 1, 1) & \dots & \mathcal{S}_{1,k} & \dots & \mathcal{S}_{1,T} \\
    \vdots           &     \vdots & \ddots & \vdots & \dots & \vdots \\
    \text{podcast}_k & \mathcal{S}_{k,1} & \dots & (1, 1, 1) & \dots & \mathcal{S}_{k,T} \\
    \vdots & \vdots & \dots & \vdots & \ddots & \vdots \\
    \text{podcast}_T & \mathcal{S}_{T,1} & \dots & \mathcal{S}_{T,k} & \dots & (1, 1, 1) \\
\end{array}
```

where $\mathcal{S}_{i,j} = ( \text{NTFS}(\mathbf{x_i}, \mathbf{x_j}), \text{JTS}(\mathbf{x_i}, \mathbf{x_j}), \text{WTDS}(\mathbf{x_i}, \mathbf{x_j}) )$

### Recommendation System

Suppose an arbitrary podcast $k$ is chosen, for which an $n$-recommendation needs to be generated from a list of $T$ podcasts:

```math
\begin{array}{cccccc}
    & \text{podcast}_1 & \dots & \text{podcast}_k & \dots & \text{podcast}_T \\
    & \mathcal{S}_{1,k}  & \dots & (1,1,1) & \dots & \mathcal{S}_{1,T} \\
\end{array}
```

Next, we quantify dissimilarity by computing the euclidean 2-norm distance with respect to podcast $k$:

```math
d_{ij} = ||(1,1,1) - \mathcal{S}_{ij}||_2 = \sqrt{\big(1 - \text{NTFS}(\mathbf{x_i}, \mathbf{x_j})\big)^2 + \big(1 - \text{JTS}(\mathbf{x_i}, \mathbf{x_j})\big)^2 + \big(1 - \text{WTDS}(\mathbf{x_i}, \mathbf{x_j})\big)^2}
```

Finally, we sort by distance (lowest to highest) and report the $n$-closest podcasts. Each reported podcast represents those whose description match most closely in direction, shared content coverage, and diversity of content to podcast $k$, ensuring tailored recommendations for enhancing user engagement.
