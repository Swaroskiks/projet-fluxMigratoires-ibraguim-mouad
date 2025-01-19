"""Dash Application to Visualize Migratory Species Flows"""

from config import HOST, PORT, DEBUG
from dash import Dash, html, page_container
import dash_bootstrap_components as dbc
from src.components import create_header, create_footer
from src.utils import download_all_species_data, clean_all_species_data

# ----- Downloading and Cleaning Data -----
download_all_species_data()
clean_all_species_data()

# ----- Creating the Dash Application -----
app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    assets_folder='assets',     # Path to static resources, including species images
    use_pages=True,             # Enable dynamic page management
    pages_folder='src/pages'    # Path to the folder containing pages
)

app.title = "Flux Migratoires"  # Application title

# ----- Defining the Layout -----
app.layout = html.Div([
    create_header(),            # Application header
    page_container,             # Dynamic page content
    create_footer()             # Application footer
])

# ----- Main Entry Point -----
if __name__ == '__main__':
    # Launch the Dash server with the configurations specified in the config file
    app.run_server(host=HOST, port=PORT, debug=DEBUG)