
import dash
from dash import dcc, html

# Create the Dash app
app = dash.Dash(
    __name__,
    use_pages=True,
    suppress_callback_exceptions=True
)

# App layout
app.layout = html.Div(
    children=[
        dcc.Location(id="url"),  # Tracks the current page
        dash.page_container,     # Dynamically loads the current page content
    ]
)

if __name__ == "__main__":
    app.run_server(debug=True, dev_tools_silence_routes_logging=False)
