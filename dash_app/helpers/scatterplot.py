import os
import numpy as np
import pandas as pd
import plotly.express as px

# Helper paths
helpers_path = './dash_app/helpers/'

# Load similarity matrices and metadata
ntfs = np.load(os.path.join(helpers_path, 'ntfs.npy'))
jts = np.load(os.path.join(helpers_path, 'jts.npy'))
wtds = np.load(os.path.join(helpers_path, 'wtds.npy'))

podcast_metadata = pd.read_csv(
    "https://raw.githubusercontent.com/Stochastic1017/Spotify-Podcast-Clustering/refs/heads/main/data/cleaned_podcast_details_english_colors.csv"
)
podcast_ids = podcast_metadata["podcast_id"].tolist()


def generate_scatter_plot(selected_podcast_id):
    """
    Generate a 3D scatter plot for a selected podcast, excluding itself and
    highlighting proximity using a gradient color scheme.
    """
    selected_podcast_index = podcast_ids.index(selected_podcast_id)

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
    print("Closest Podcasts:")
    print(closest_podcasts[['podcast_name', 'distance']])

    # Plot with Plotly Express using gradient color
    fig = px.scatter_3d(
        plot_data,
        x='NTFS',
        y='JTS',
        z='WTDS',
        color='distance',  # Gradient color based on distance
        color_continuous_scale='Viridis',  # Darker = closer
        hover_data={
            'podcast_name': True,
            'podcast_publisher': True,
            'podcast_total_episodes': True,
            'podcast_explicit': True,
            'podcast_genre': True,
            'distance': True,
        },
        title=f"Similarity Metrics for Podcast: {selected_podcast_id}",
        labels={
            'NTFS': 'Normalized Total Feature Similarity',
            'JTS': 'Joint Topic Similarity',
            'WTDS': 'Weighted Topic Diversity Score',
            'distance': 'Distance to Selected Podcast'
        },
        template='plotly_dark'
    )

    # Customize layout
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='white',
        title_font_color='white',
        margin=dict(l=0, r=0, t=30, b=0)
    )

    return fig
