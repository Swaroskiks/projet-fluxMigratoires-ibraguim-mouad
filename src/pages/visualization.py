import json
import dash
from dash import html, dcc, callback, Input, Output, register_page
import dash_bootstrap_components as dbc

from src.components import create_map, create_species_select
from src.utils import load_species_metadata, load_species_data_from_csv

register_page(__name__, path='/visualization')

def layout() -> html.Div:
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

@callback(
    [Output("current-data", "data"),
     Output("app-state", "data")],
    [Input({'type': 'species-button', 'index': dash.dependencies.ALL}, 'n_clicks'),
     Input({'type': 'map-mode', 'mode': dash.dependencies.ALL}, 'n_clicks')],
    [Input("app-state", "data")],
    prevent_initial_call=True
)
def update_data_and_state(species_clicks, mode_clicks, current_state):
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update, dash.no_update

    trigger = ctx.triggered[0]['prop_id']
    current_state = current_state or {'view_mode': 'scatter'}

    if 'map-mode' in trigger:
        button_id = json.loads(trigger.split('.')[0])
        current_state['view_mode'] = button_id['mode']
        return dash.no_update, current_state

    elif 'species-button' in trigger:
        button_id = json.loads(trigger.split('.')[0])
        selected_idx = button_id['index']
        species_data = load_species_metadata()
        species_name = species_data['datasets'][selected_idx]['scientific_name'].lower().replace(' ', '_')
        df = load_species_data_from_csv(species_name)
        return df.to_dict('records'), current_state

    return dash.no_update, dash.no_update