
from dash import html, dcc, Input, Output, callback
import dash

dash.register_page(__name__, path="/")

layout = html.Div(
    id="intro-page",
    style={
        'backgroundColor': 'black',
        'height': '100vh',
        'display': 'flex',
        'flexDirection': 'column',
        'alignItems': 'center',
        'justifyContent': 'center',
        'position': 'absolute',
        'top': '0',
        'left': '0',
        'width': '100%',
        'zIndex': 2,
        'transition': 'opacity 1s ease-in-out',
    },
    children=[
        
        # Video Element
        html.Video(
            id="intro-video",
            src='/assets/SpotifyLogo.mp4',
            autoPlay=True,
            controls=False,
            loop=False,
            muted=True,
            style={'width': '50%'},
        ),
        
        # Interval to trigger navigation
        dcc.Interval(
            id="redirect-timer",
            interval=4000,
            n_intervals=0,
            max_intervals=1,
        ),
    ]
)

# Callback to navigate to the main page after the interval
@callback(
    Output("url", "pathname"),
    Input("redirect-timer", "n_intervals"),
    prevent_initial_call=True,
)
def navigate_to_main(n_intervals):
    if n_intervals > 0:
        return "/main"
    return "/"
