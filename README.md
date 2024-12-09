# Clustering Spotify Podcasts with NLP-Driven Insights

## Introduction

Spotify has already developed several music-specific metrics/derived features about a particular track/music, specifically: (a) acousticness, (b) danceability, (c) energy, (d) instrumentalness, (e) speechiness, and (f) valence.
All these metrics are in the range of [0,1] and can be used to cluster users based on their musical taste. This project is meant to construct similar informative metrics for Spotify’s podcast data, and create a novel recommendation system based on these metrics.

## Data Collection using Spotify API

The [`fetch_top_podcast.py`](https://github.com/Stochastic1017/Spotify-Podcast-Clustering/blob/main/spotify_api/fetch_top_podcast.py) uses selenium to scrape all top 50 podcasts from [here](https://podcastcharts.byspotify.com/) for each genre. This gives us a total of 850 podcasts. Next, the [`fetch_podcast_details.py`](https://github.com/Stochastic1017/Spotify-Podcast-Clustering/blob/main/spotify_api/fetch_podcast_details.py) uses the spotify api to scrape details from each of the 850 podcasts, and those podcasts **not** in english are removed, leaving us with a podcast count of 818. Finally, the [`fetch_episode_details.py`](https://github.com/Stochastic1017/Spotify-Podcast-Clustering/blob/main/spotify_api/fetch_episode_details.py) uses spotify api to scrape details for all episodes, giving us a total of 284481 episodes.

## Description cleanup and tokenization

The python library `nltk` (natural language toolkit) is used to clean and tokenize the episode descriptions. In summary, the following cleaning is done using [`clean\_description.py`](https://github.com/Stochastic1017/Spotify-Podcast-Clustering/blob/main/tokenization/clean_description.py):

* *Text Normalization:* accent removal, lowercasing, whitespace normalization.
* *Sentence-Level Cleaning:* contraction expansion, URL removal, promotional density check.
* *Token-Level Cleaning:* lemmatization, stopword removal, promotional keyword removal, character validation, length check, dictionary validation, special character removal.

