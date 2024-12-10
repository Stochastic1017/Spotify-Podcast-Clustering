from dash import html, dcc, callback, Output, Input
from helpers.scatterplot import generate_plot
import dash
import pandas as pd

# Register the page with a custom path
dash.register_page(__name__, path="/main")

# Load podcast data
podcast_data = pd.read_csv(
    "https://github.com/Stochastic1017/Spotify-Podcast-Clustering/raw/refs/heads/main/data/cleaned_podcast_details_english_colors.csv"
)

# Exclude specific podcasts based on conditions
excluded_podcast_ids = ["24PzTknDMWxNTA2KExjHi5", "3K0KOwZ9OiFML5E9P4dvEZ"]  # Replace with actual IDs
podcast_data = podcast_data[~podcast_data["podcast_id"].isin(excluded_podcast_ids)]


# Extract podcast options for dropdown
podcast_options = sorted(
    [{"label": row["podcast_name"], "value": row["podcast_id"]}
     for row in podcast_data[["podcast_name", "podcast_id"]].to_dict(orient="records")],
    key=lambda x: x["label"]
)

# CSS for consistent styling
app_css = {
    'background': 'linear-gradient(135deg, #121212 0%, #1E1E1E 100%)',
    'fontFamily': '"Circular", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif',
}

# Layout definition
layout = html.Div(
    style={
        **app_css,
        'display': 'flex',
        'flexDirection': 'column',
        'height': '100vh',
        'color': 'white',
        'padding': '20px',
        'overflow': 'hidden',
    },
    children=[
        # Header Section
        html.Div(
            id="header-section",
            style={
                'display': 'flex',
                'alignItems': 'center',
                'justifyContent': 'space-between',
                'marginBottom': '20px',
                'padding': '0 20px',
            },
            children=[
                # Spotify Logo
                html.Img(
                    src="https://raw.githubusercontent.com/Stochastic1017/Spotify-Podcast-Clustering/refs/heads/main/dash_app/assets/SpotifyLogo.png",
                    alt="Spotify Logo",
                    style={
                        'width': '250px',
                        'height': 'auto',
                    },
                ),
                # Dropdown for podcast selection
                dcc.Dropdown(
                    id="podcast-dropdown",
                    options=podcast_options,
                    placeholder="Search for a podcast...",
                    style={
                        'width': '300px',
                        'height': '50px',
                        'backgroundColor': '#282828',
                        'color': '#1DB954',
                        'borderRadius': '20px',
                        'textAlign': 'left',
                    },
                    optionHeight=50,
                    className='custom-dropdown',
                ),
            ],
        ),
        # Main Content
        html.Div(
            id="main-content",
            style={
                'display': 'flex',
                'flex': '1',
                'gap': '20px',
                'overflow': 'hidden',
            },
            children=[
                # Podcast Details
                html.Div(
                    id="podcast-details-container",
                    style={
                        'flexBasis': '20%',
                        'maxWidth': '300px',
                        'backgroundColor': '#282828',
                        'borderRadius': '15px',
                        'padding': '10px',
                        'overflowY': 'auto',
                        'overflowX': 'auto',
                        'boxShadow': '0 10px 20px rgba(0,0,0,0.2)',
                    },
                ),
                # Scatter Plot with Loading Animation
                html.Div(
                    id="scatter-plot-container",
                    children=[
                        dcc.Loading(
                            id="loading-scatter-plot",
                            type="default",
                            color="#1DB954",
                            children=html.Div(id="scatter-plot-content"),
                        )
                    ],
                    style={
                        "flex": "1",
                        "backgroundColor": "#282828",
                        "borderRadius": "10px",
                        "padding": "10px",
                        "display": "flex",
                        "flexDirection": "column",
                        "alignItems": "center",
                        "justifyContent": "center",
                        'overflowY': 'auto',
                        'overflowX': 'auto',
                        "boxShadow": "0 10px 20px rgba(0,0,0,0.2)",
                        "position": "relative",
                    },
                ),
            ],
        ),
        # Footer Section
        html.Footer(
            id="footer-section",
            style={
                'backgroundColor': '#1E1E1E',
                'padding': '10px',
                'textAlign': 'center',
                'color': '#B3B3B3',
                'fontSize': '0.9rem',
                'marginTop': 'auto',
                'borderTop': '1px solid #282828',
                'overflowY': 'auto',
                'overflowX': 'auto',
            },
            children=[
                html.P("Developed by Shrivats Sudhir | Contact: stochastic1017@gmail.com"),
                html.P(
                    [
                        "GitHub Repository: ",
                        html.A(
                            "Spotify Podcast Clustering",
                            href="https://github.com/Stochastic1017/Spotify-Podcast-Clustering",
                            target="_blank",
                            style={'color': '#1DB954', 'textDecoration': 'none'}
                        ),
                    ]
                ),
                html.P(
                    [
                        "Introduction Spotify Animation: ",
                        html.A(
                            "【Logo Animation】ポヨンポヨンとスポティファイ【Spotify】",
                            href="https://www.youtube.com/watch?v=cB8JW-uLuC4",
                            target="_blank",
                            style={'color': '#1DB954', 'textDecoration': 'none'}
                        ),
                    ]
                )
            ],
        ),
    ],
)

# Callback to update podcast details
@callback(
    Output("podcast-details-container", "children"),
    Output("podcast-details-container", "style"),
    Input("podcast-dropdown", "value"),
)
def update_podcast_details(selected_podcast_id):
    # Default style
    default_style = {
        'flexBasis': '20%',
        'maxWidth': '300px',
        'backgroundColor': '#282828',
        'borderRadius': '15px',
        'padding': '20px',
        'overflowY': 'auto',
        'boxShadow': '0 10px 20px rgba(0,0,0,0.2)',
        'border': '2px solid #282828',
        'transition': 'all 0.5s ease-in-out',
    }

    if not selected_podcast_id:
        return html.Div(
        ), default_style

    # Fetch details for selected podcast
    podcast = podcast_data[podcast_data["podcast_id"] == selected_podcast_id].iloc[0]
    dominant_color = podcast["podcast_dominant_color"]
    word_cloud_src = f"https://raw.githubusercontent.com/Stochastic1017/Spotify-Podcast-Clustering/refs/heads/main/wordclouds/{podcast['podcast_id']}.png"

    details = html.Div(
        children=[
            html.Img(
                src=podcast["podcast_image_url"],
                style={
                    'width': '300px',
                    'height': '300px',
                    'objectFit': 'cover',
                    'borderRadius': '15px',
                    'marginBottom': '20px',
                    'boxShadow': '0 10px 20px rgba(0,0,0,0.3)',
                },
            ),
            html.H3(
                podcast["podcast_name"],
                style={
                    'color': '#1DB954',
                    'marginBottom': '10px',
                    'fontSize': '1.5rem',
                }
            ),
            html.P(f"Publisher: {podcast['podcast_publisher']}", style={'color': '#B3B3B3'}),
            html.P(f"{podcast['podcast_description']}", style={'color': '#B3B3B3'}),
            html.P(f"Total Episodes: {podcast['podcast_total_episodes']}", style={'color': '#B3B3B3'}),
            html.P(f"Genre: {podcast['podcast_genre']}", style={'color': '#B3B3B3'}),
            html.Img(
                src=word_cloud_src,
                alt="Word Cloud",
                style={
                    'width': '100%',
                    'marginTop': '20px',
                    'borderRadius': '15px',
                    'boxShadow': '0 10px 20px rgba(0,0,0,0.3)',
                },
            ),
            html.Div(
                children=[
                    dcc.Link(
                        "Listen on Spotify",
                        href=podcast["podcast_url"],
                        target="_blank",
                        style={
                            'backgroundColor': '#1DB954',
                            'color': 'white',
                            'padding': '10px 20px',
                            'borderRadius': '25px',
                            'textDecoration': 'none',
                            'fontWeight': 'bold',
                            'transition': 'transform 0.2s',
                            'display': 'inline-block',
                        },
                        className='click-button'
                    ),
                ],
                style={
                    'display': 'flex',
                    'justifyContent': 'center',
                    'gap': '10px',
                    'marginTop': '20px',
                }
            )
        ],
        style={
            'display': 'flex',
            'flexDirection': 'column',
            'alignItems': 'center',
            'textAlign': 'center',
        }
    )

    updated_style = {**default_style, 'border': f"2px solid {dominant_color}"}
    return details, updated_style

# Callback to update scatter plot
@callback(
    Output("scatter-plot-content", "children"),
    Input("podcast-dropdown", "value"),
)
def update_scatter_plot(selected_podcast_id):
    if not selected_podcast_id:
        return html.Div(
            "If plots or tables don't fit properly, press Ctrl - or Ctrl + to adjust the zoom level until the layout looks satisfactory.",
            style={'color': '#B3B3B3'}
        )

    return dcc.Graph(figure=generate_plot(selected_podcast_id))
