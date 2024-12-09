
import os
import sys

# Append current directory to system path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
from io import BytesIO


# Helper function to load .npy files from GitHub
def load_npy_from_github(url):
    response = requests.get(url)
    response.raise_for_status()  # Raise an error for failed requests
    return np.load(BytesIO(response.content))

# URLs for data
ntfs_url = "https://github.com/Stochastic1017/Spotify-Podcast-Clustering/raw/refs/heads/main/dash_app/helpers/ntfs.npy"
jts_url = "https://github.com/Stochastic1017/Spotify-Podcast-Clustering/raw/refs/heads/main/dash_app/helpers/jts.npy"
wtds_url = "https://github.com/Stochastic1017/Spotify-Podcast-Clustering/raw/refs/heads/main/dash_app/helpers/wtds.npy"
metadata_url = "https://raw.githubusercontent.com/Stochastic1017/Spotify-Podcast-Clustering/refs/heads/main/data/cleaned_podcast_details_english_colors.csv"

# Load data
ntfs = load_npy_from_github(ntfs_url)
jts = load_npy_from_github(jts_url)
wtds = load_npy_from_github(wtds_url)
podcast_metadata = pd.read_csv(metadata_url)
podcast_ids = podcast_metadata["podcast_id"].tolist()

def generate_plot(selected_podcast_id):
    """
    Generate a combined subplot figure with:
    1. A 3D scatter plot (using plotly.express) showing podcast similarities.
    2. A table listing the 5 closest podcasts with associated details.
    """
    selected_podcast_index = podcast_ids.index(selected_podcast_id)
    selected_podcast_name = podcast_metadata[podcast_metadata['podcast_id'] == selected_podcast_id]['podcast_name'].iloc[0]

    # Extract similarity metrics for the selected podcast
    ntfs_row = ntfs[selected_podcast_index]
    jts_row = jts[selected_podcast_index]
    wtds_row = wtds[selected_podcast_index]

    # Create a DataFrame for plotting
    plot_data = pd.DataFrame({
        'podcast_id': podcast_ids,
        'NTFS': ntfs_row,
        'JTS': jts_row,
        'WTDS': wtds_row
    })

    # Compute Euclidean distances from the selected podcast
    plot_data['distance'] = np.sqrt(
        (plot_data['NTFS'] - 1)**2 +
        (plot_data['JTS'] - 1)**2 +
        (plot_data['WTDS'] - 1)**2
    )

    # Remove the selected podcast (distance = 0)
    plot_data = plot_data[plot_data['podcast_id'] != selected_podcast_id]

    # Merge with metadata for hover data
    plot_data = plot_data.merge(podcast_metadata, on='podcast_id', how='left')

    # Sort by distance to find closest podcasts
    closest_podcasts = plot_data.nsmallest(5, 'distance')

    # Create the 3D scatter plot using graph_objects instead of express
    scatter_fig = go.Figure(data=[
        go.Scatter3d(
            x=plot_data['NTFS'],
            y=plot_data['JTS'],
            z=plot_data['WTDS'],
            mode='markers',
            marker=dict(
                size=5,
                color=plot_data['distance'],
                colorscale='plasma_r',
                opacity=0.8,
                colorbar=dict(title='Distance')
            ),
            text=plot_data['podcast_name'],
            hoverinfo='text'
        )
    ])
    
    # Details Table
    table_fig = go.Table(
        header=dict(
            values=["<b>Podcast Name</b>", "<b>Distance</b>", "<b>Publisher</b>", "<b>Genre</b>", "<b>Total Episodes</b>"],
            fill_color='darkslategray',
            font=dict(color='white', size=14),
            align='left',
            height=40
        ),
        cells=dict(
            values=[
                closest_podcasts['podcast_name'],
                closest_podcasts['distance'].round(3),
                closest_podcasts['podcast_publisher'],
                closest_podcasts['podcast_genre'],
                closest_podcasts['podcast_total_episodes']
            ],
            fill_color='lightgray',
            font=dict(color='black', size=13),
            align='left',
            height=50
        )
    )

    # Combine Scatter Plot and Table into Subplots
    fig = make_subplots(
        rows=1, cols=2,
        column_widths=[0.6, 0.4],
        specs=[[{"type": "scatter3d"}, {"type": "table"}]],
        subplot_titles=[f"Podcast Similarity Analysis: {selected_podcast_name}\n", "Recommended Podcasts\n"]
    )

    # Add scatter plot
    fig.add_trace(scatter_fig.data[0], row=1, col=1)

    # Add table
    fig.add_trace(table_fig, row=1, col=2)

    # Update layout for combined figure
    fig.update_layout(
        title="",
        template='plotly_dark',
        height=850,
        width=1450,
        title_font_color='white',
        font_color='white',
        margin=dict(l=20, r=20, t=50, b=20),
        scene = dict(
            xaxis = dict(
                title = dict(
                    text = 'Normalized Total Feature Similarity'
                )),
            yaxis = dict(
                title = dict(
                    text = 'Joint Topic Similarity'
            )),
            zaxis = dict(
                title = dict(
                    text = 'Weighted Topic Diversity Score'
                )
            )
            )
        )

    return fig
