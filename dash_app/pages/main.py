
from dash import html, dcc, callback, Output, Input
from helpers.scatterplot import generate_plot
import dash
import pandas as pd

# Register the page with a custom path
dash.register_page(__name__, path="/main")

# Load the podcast data
podcast_data =  pd.read_csv(
    "https://github.com/Stochastic1017/Spotify-Podcast-Clustering/raw/refs/heads/main/data/cleaned_podcast_details_english_colors.csv"
)

# Extract relevant fields and sort options
podcast_options = sorted(
    [{"label": record["podcast_name"], "value": record["podcast_id"]} for record in podcast_data[["podcast_name", "podcast_id"]].to_dict(orient="records")],
    key=lambda x: x["label"]
)

# Custom CSS for styling
app_css = {
    'background': 'linear-gradient(135deg, #121212 0%, #1E1E1E 100%)',
    'fontFamily': '"Circular", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif',
}

# Main Layout
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
                    }
                ),
                # Podcast Dropdown
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
            ]
        ),

        # Main Content Area
        html.Div(
            style={
                'display': 'flex',
                'flex': '1',
                'gap': '20px',
                'overflow': 'hidden',
            },
            children=[
                # Podcast Details Container
                html.Div(
                    id="podcast-details-container",
                    style={
                        'flexBasis': '20%',
                        'maxWidth': '300px',
                        'backgroundColor': '#282828',
                        'borderRadius': '15px',
                        'padding': '20px',
                        'overflowY': 'auto',
                        'boxShadow': '0 10px 20px rgba(0,0,0,0.2)',
                    },
                ),

                # Scatter Plot Container with Tab Toggle for 2D/3D View
                html.Div(
                    id="scatter-plot-container",
                    children=[
                        html.Div(
                            style={
                                "color": "#282828",
                                "width": "100%",
                                "height": "100%",
                                "textAlign": "center",
                                "fontSize": "1.2rem",
                                "marginTop": "50px"
                            }
                        )
                    ],
                    style={
                        "flex": "1",
                        "backgroundColor": "#282828",
                        "borderRadius": "15px",
                        "padding": "20px",
                        "display": "flex",
                        "flexDirection": "column",
                        "alignItems": "center",
                        "justifyContent": "flex-start",
                        "boxShadow": "0 10px 20px rgba(0,0,0,0.2)",
                    },
                ),

            ]
        ),
    ]
)

@callback(
    Output("podcast-details-container", "children"),
    Output("podcast-details-container", "style"),
    Input("podcast-dropdown", "value"),
)
def update_podcast_details(selected_podcast):
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
    
    if not selected_podcast:
        return (
            html.Div(
                "Select a podcast to view details.",
                style={'color': '#B3B3B3', 'textAlign': 'center'}
            ),
            default_style  # Return the default style
        )

    # Fetch podcast details
    podcast = podcast_data[podcast_data["podcast_id"] == selected_podcast].iloc[0]
    dominant_color = podcast["podcast_dominant_color"]

    # Generate word cloud image URL
    word_cloud_src = f"https://raw.githubusercontent.com/Stochastic1017/Spotify-Podcast-Clustering/refs/heads/main/wordclouds/{podcast['podcast_id']}.png"

    # Podcast details content with word cloud and buttons
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

            # Add Word Cloud and Buttons
            html.Div(
                children=[
                    html.Img(
                        src=word_cloud_src,
                        alt="Word Cloud",
                        style={
                            'width': '100%',
                            'height': 'auto',
                            'marginTop': '20px',
                            'borderRadius': '15px',
                            'boxShadow': '0 10px 20px rgba(0,0,0,0.3)',
                        }
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
        ],
        style={'textAlign': 'center'}
    )

    # Update container style with dynamic border and box shadow
    container_style = {
        **default_style,
        'border': f"2px solid {dominant_color}",
    }

    return details, container_style

@callback(
    Output("scatter-plot-container", "children"),
    Input("podcast-dropdown", "value"),
)
def update_scatter_plot(selected_podcast_id):
    if not selected_podcast_id:
        return

    return dcc.Graph(figure=generate_plot(selected_podcast_id))
