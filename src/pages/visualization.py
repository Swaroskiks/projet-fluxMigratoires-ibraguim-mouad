"""Migration Visualization Page

This page allows users to visualize the movements of a species on an interactive map.

Main Features:
- **Species Selection**: Users can choose the species whose migration data they want to explore.
- **Interactive Map**: Visualize movements with several display modes:
    - Points: Each recorded position is represented as a point on the map.
    - Density: A heatmap identifies areas with high concentration.
    - Trajectory: Follow individual animals' migration paths.
- **Visualization Controls**: Easily switch display modes to better understand migratory behaviors.
"""

import json
import dash
from dash import html, dcc, callback, Input, Output, register_page
import dash_bootstrap_components as dbc
from src.components import create_map, create_species_select
from src.utils import load_species_metadata, load_species_data_from_csv

# ----- Registering the page -----
register_page(__name__, path='/visualization')

# ----- Visualization page layout -----
def layout() -> html.Div:
    """Creates the layout for the visualization page.
    
    This function assembles the various components of the page:
    - Stores to manage the application's state
    - Page title
    - Species selector
    - Interactive map

    Returns:
        html.Div: Complete structure of the visualization page.
    """
    return dbc.Container([
        dcc.Store(id='app-state', data={'view_mode': 'scatter'}),
        dcc.Store(id='current-data', storage_type='memory'),

        dbc.Row([
            dbc.Col(html.H1("Visualisation des Migrations", className="text-center mb-4 mt-4"), width=12),
            dbc.Col(create_species_select(), width=3),
            dbc.Col([
                create_map()
            ], width=9)
        ])
    ], fluid=True)

# ----- User interaction handling -----
@callback(
    Output("current-data", "data"),
    Input({'type': 'species-button', 'index': dash.dependencies.ALL}, 'n_clicks'),
    prevent_initial_call=True
)
def update_species_data(species_clicks: list) -> dict:
    """Loads the data for the selected species.

    Args:
        species_clicks (list): Clicks on the species buttons.

    Returns:
        dict: Data for the selected species.
    """
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update

    button_id = json.loads(ctx.triggered[0]['prop_id'].split('.')[0])
    selected_idx = button_id['index']
    species_data = load_species_metadata()
    species_name = species_data['datasets'][selected_idx]['scientific_name'].lower().replace(' ', '_')
    df = load_species_data_from_csv(species_name)
    return df.to_dict('records')

# ----- Callback for changing map mode -----
@callback(
    Output("app-state", "data"),
    Input({'type': 'map-mode', 'mode': dash.dependencies.ALL}, 'n_clicks'),
    prevent_initial_call=True
)
def update_map_mode(mode_clicks: list) -> dict:
    """Updates the map visualization mode.

    Args:
        mode_clicks (list): Clicks on the mode buttons.

    Returns:
        dict: New state with the selected visualization mode.
    """
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update

    button_id = json.loads(ctx.triggered[0]['prop_id'].split('.')[0])
    new_mode = button_id['mode']
    return {'view_mode': new_mode}