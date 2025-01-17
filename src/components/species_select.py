import json
import dash
from dash import html, callback, Input, Output, State
import dash_bootstrap_components as dbc
from src.utils import load_species_metadata

def create_species_select() -> html.Div:
    data = load_species_metadata()

    species_cards = [
        dbc.Button(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            html.Img(
                                src=f"assets/images/species/{species['scientific_name'].replace(' ', '_').lower()}.webp",
                                alt=species["name"],
                                style={"height": "60px", "width": "60px", "borderRadius": "5px"},
                            ),
                            width="auto"
                        ),
                        dbc.Col(
                            [
                                html.Strong(species["name"]),
                                html.Div(species["scientific_name"], style={"fontStyle": "italic", "fontSize": "small"}),
                                html.Div(species["description"], style={"fontSize": "small"}),
                            ]
                        )
                    ],
                    align="center"
                )
            ],
            id={"type": "species-button", "index": idx},
            color="light",
            className="w-100 mb-2",
            style={"textAlign": "left"}
        )
        for idx, species in enumerate(data["datasets"])
    ]

    return html.Div([
        html.H5("Sélectionnez une espèce :"),
        html.Div(species_cards, style={"overflowY": "auto", "height": "70vh"})
    ])

@callback(
    Output({'type': 'species-button', 'index': dash.dependencies.ALL}, 'color'),
    Input({'type': 'species-button', 'index': dash.dependencies.ALL}, 'n_clicks'),
    State({'type': 'species-button', 'index': dash.dependencies.ALL}, 'id'),
    prevent_initial_call=True
)
def update_species_selection(species_clicks, species_ids):
    ctx = dash.callback_context
    
    if not ctx.triggered:
        return dash.no_update
    
    trigger_id = json.loads(ctx.triggered[0]['prop_id'].split('.')[0])
    colors = ['light' for _ in species_ids]
    
    if trigger_id['type'] == 'species-button':
        selected_idx = trigger_id['index']
        colors[selected_idx] = 'primary'

    return colors