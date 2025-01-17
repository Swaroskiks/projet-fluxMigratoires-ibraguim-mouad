from config import HOST, PORT, DEBUG
from dash import Dash, html, page_container
import dash_bootstrap_components as dbc
from src.components import create_header, create_footer
from src.utils import download_all_species_data, clean_all_species_data

download_all_species_data()
clean_all_species_data()

app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    assets_folder='assets',
    use_pages=True,
    pages_folder='src/pages'
)

app.title = "Flux Migratoires"

app.layout = html.Div([
    create_header(),
    page_container,
    create_footer()
])

if __name__ == '__main__':
    app.run_server(host=HOST, port=PORT, debug=DEBUG)