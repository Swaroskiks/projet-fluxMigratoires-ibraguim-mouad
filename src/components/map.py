import json
import dash
from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
from pathlib import Path

def create_map_controls() -> html.Div:
    """Crée les boutons de contrôle de la carte."""
    return html.Div(
        [
            dbc.ButtonGroup(
                [
                    dbc.Button(
                        "Points",
                        id={"type": "map-mode", "mode": "scatter"},
                        color="primary",
                        n_clicks=0,
                    ),
                    dbc.Button(
                        "Densité",
                        id={"type": "map-mode", "mode": "density"},
                        color="secondary",
                        n_clicks=0,
                    ),
                    dbc.Button(
                        "Trajectoire",
                        id={"type": "map-mode", "mode": "trajectory"},
                        color="secondary",
                        n_clicks=0,
                    ),
                ],
                className="mb-3",
            )
        ]
    )

@callback(
    Output({'type': 'map-mode', 'mode': dash.dependencies.ALL}, 'color'),
    Input({'type': 'map-mode', 'mode': dash.dependencies.ALL}, 'n_clicks'),
    State({'type': 'map-mode', 'mode': dash.dependencies.ALL}, 'id'),
    prevent_initial_call=True
)
def update_map_mode(mode_clicks, mode_ids):
    ctx = dash.callback_context

    if not ctx.triggered:
        return dash.no_update

    trigger_id = json.loads(ctx.triggered[0]['prop_id'].split('.')[0])
    colors = ['secondary' for _ in mode_ids]

    if trigger_id['type'] == 'map-mode':
        mode = trigger_id['mode']
        for idx, mode_id in enumerate(mode_ids):
            colors[idx] = 'primary' if mode_id['mode'] == mode else 'secondary'

    return colors

def generate_empty_map_figure():
    fig = px.scatter_mapbox(
        pd.DataFrame({'location_lat': [], 'location_long': []}),
        lat="location_lat",
        lon="location_long",
        zoom=2
    )
    fig.update_layout(
        mapbox_style="open-street-map",
        margin={"l": 0, "r": 0, "t": 0, "b": 0},
        showlegend=False,
    )
    return fig

def create_map() -> html.Div:
    """Assemble les contrôles et la carte."""
    fig = generate_empty_map_figure() 

    return html.Div(
        [
            create_map_controls(),
            dcc.Graph(
                id="map",
                figure=fig,
                style={
                    "height": "67vh",
                    "borderRadius": "15px",
                    "boxShadow": "0 4px 8px rgba(0, 0, 0, 0.1)",
                },
            ),
        ]
    )

def generate_map_figure(
    df: pd.DataFrame, mode: str = "scatter", selected_point: pd.Series = None
):
    """Génère la figure de la carte selon le mode sélectionné."""
    if mode == "scatter":
        fig = px.scatter_mapbox(
            df, lat="location_lat", lon="location_long", hover_name="timestamp", zoom=3
        )
        if selected_point is not None:
            fig.add_scattermapbox(
                lat=[selected_point["location_lat"]],
                lon=[selected_point["location_long"]],
                mode="markers",
                marker=dict(size=15, color="yellow"),
                name="Point sélectionné",
            )
    elif mode == "density":
        fig = px.density_mapbox(
            df, lat="location_lat", lon="location_long", radius=10, zoom=3
        )
    else:  # mode == "trajectory"
        grouped = (
            df.groupby(df.index // 20)
            .agg({"location_lat": "mean", "location_long": "mean"})
            .reset_index()
        )
        fig = px.line_mapbox(grouped, lat="location_lat", lon="location_long", zoom=3)

    fig.update_layout(
        mapbox_style="open-street-map",
        margin={"l": 0, "r": 0, "t": 0, "b": 0},
        showlegend=False,
    )
    return fig

@callback(
    Output("map", "figure"),
    [Input("app-state", "data"),
     Input("current-data", "data")],
    prevent_initial_call=True
)
def update_map(app_state, current_data):
    """Met à jour la carte en fonction du mode et des données."""
    if not app_state or not current_data:
        return dash.no_update
    
    df = pd.DataFrame(current_data)
    mode = app_state.get('view_mode', 'scatter') if app_state else 'scatter'
    
    return generate_map_figure(df, mode)