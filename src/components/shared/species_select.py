"""Species Selection Component.

Displays species as buttons with:
- A representative image
- Common name
- Scientific name
- A short description
"""

import json
import dash
from dash import html, callback, Input, Output, State
import dash_bootstrap_components as dbc
from src.utils import load_species_metadata


def create_species_select() -> html.Div:
    """Create the species selection component.

    Loads metadata for available species and generates a list of buttons,
    each displaying an image, common name, scientific name, and description.

    Returns:
        html.Div: Dash component containing the species selection buttons.s
    """
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
def update_species_selection(species_clicks: list, species_ids: list) -> list:
    """Update the selection state of species buttons.

    Called when a species button is clicked, this function updates the colors
    of all buttons to highlight the selected species and reset the others.

    Args:
        species_clicks: List of click counts for each species button.
        species_ids: List of IDs for each species button.

    Returns:
        list: List of colors to apply to each button ('primary' for the
              selected button, 'light' for the others).
    """
    ctx = dash.callback_context
    
    if not ctx.triggered:
        return dash.no_update
    
    trigger_id = json.loads(ctx.triggered[0]['prop_id'].split('.')[0])
    colors = ['light' for _ in species_ids]
    
    if trigger_id['type'] == 'species-button':
        selected_idx = trigger_id['index']
        colors[selected_idx] = 'primary'

    return colors