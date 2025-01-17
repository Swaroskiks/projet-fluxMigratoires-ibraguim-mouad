from dash import html, dcc
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

def create_map() -> html.Div:
    """Assemble les contrôles et la carte."""
    return html.Div(
        [
            create_map_controls(),
            dcc.Graph(
                id="map",
                figure={},
                style={
                    "height": "60vh",
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