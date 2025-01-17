import json
import dash
from dash import html, callback, Input, Output, State, register_page
import dash_bootstrap_components as dbc

from src.components import create_map, generate_map_figure, create_timeline, create_species_selector 
from src.utils import load_species_metadata, load_species_data_from_csv, state

register_page(__name__, path='/visualization')

def layout() -> html.Div:
    return dbc.Container([
        dbc.Row([
            dbc.Col(html.H1("Visualisation des Migrations", className="text-center mb-4"), width=12),
            dbc.Col(create_species_selector(), width=3),
            dbc.Col([
                create_map(),
                html.Div(id="timeline-container", className="mt-4")
            ], width=9)
        ])
    ], fluid=True)

@callback(
    [Output("map", "figure"), Output("timeline-container", "children")],
    [Input({'type': 'map-mode', 'mode': dash.dependencies.ALL}, 'n_clicks'),
     Input({'type': 'species-button', 'index': dash.dependencies.ALL}, 'n_clicks')],
    prevent_initial_call=True
)
def update_visualization(mode_clicks, species_clicks):
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update, dash.no_update

    trigger = ctx.triggered[0]['prop_id']

    if 'map-mode' in trigger:
        button_id = json.loads(trigger.split('.')[0])
        state.view_mode = button_id['mode']

    elif 'species-button' in trigger:
        button_id = json.loads(trigger.split('.')[0])
        selected_idx = button_id['index']
        species_data = load_species_metadata()
        state.selected_species = species_data['datasets'][selected_idx]['scientific_name'].lower().replace(' ', '_')

    if state.selected_species:
        df = load_species_data_from_csv(state.selected_species)
        figure = generate_map_figure(df, state.view_mode)
        timeline = create_timeline(df)
        return figure, timeline

    return dash.no_update, dash.no_update

@callback(
    [Output({'type': 'species-button', 'index': dash.dependencies.ALL}, 'style'),
     Output({'type': 'map-mode', 'mode': dash.dependencies.ALL}, 'color')],
    [Input({'type': 'species-button', 'index': dash.dependencies.ALL}, 'n_clicks'),
     Input({'type': 'map-mode', 'mode': dash.dependencies.ALL}, 'n_clicks')],
    [State({'type': 'species-button', 'index': dash.dependencies.ALL}, 'id'),
     State({'type': 'map-mode', 'mode': dash.dependencies.ALL}, 'id')],
    prevent_initial_call=True
)
def highlight_active_buttons(species_clicks, mode_clicks, species_ids, mode_ids):
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update, dash.no_update

    trigger = ctx.triggered[0]['prop_id']
    card_styles = [{'background-color': 'white'} for _ in species_ids]
    button_colors = ['secondary' for _ in mode_ids]

    if 'species-button' in trigger:
        button_id = json.loads(trigger.split('.')[0])
        card_styles[button_id['index']]['background-color'] = '#e9ecef'

    if 'map-mode' in trigger or state.view_mode:
        for idx, mode_id in enumerate(mode_ids):
            if mode_id['mode'] == state.view_mode:
                button_colors[idx] = 'primary'

    return card_styles, button_colors