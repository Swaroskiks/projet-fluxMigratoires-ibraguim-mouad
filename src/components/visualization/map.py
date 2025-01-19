"""Map Visualization Component for Migration Data.

Features:
- Points Mode: Visualization of individual positions colored by season.
- Density Mode: Display areas of concentration with a density scale.
- Trajectory Mode: Trace individual movements with anomaly filtering.
"""

from typing import Dict, Any, List, Optional
import json
import dash
from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import math
from datetime import datetime

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate the distance in kilometers between two geographic points.

    Args:
        lat1 (float): Latitude of the first point.
        lon1 (float): Longitude of the first point.
        lat2 (float): Latitude of the second point.
        lon2 (float): Longitude of the second point.

    Returns:
        float: Distance in kilometers between the two points.
    """
    R = 6371  # Radius of the Earth in kilometers
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    return R * c

def create_map_controls() -> html.Div:
    """Create the controls for switching map visualization modes.

    Returns:
        html.Div: Dash component with buttons for mode selection.
    """
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
def update_map_mode(mode_clicks: List[int], mode_ids: List[Dict[str, Any]]) -> List[str]:
    """Update the button colors to indicate the selected map mode.

    Args:
        mode_clicks (List[int]): Click counts for each button.
        mode_ids (List[Dict[str, Any]]): Identifiers of the buttons.

    Returns:
        list: Colors for the buttons ('primary' for selected, 'secondary' for others).
    """
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

def generate_empty_map_figure() -> go.Figure:
    """Generate a basic empty map figure.

    Returns:
        go.Figure: Plotly figure with an empty map.
    """
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
    """Create the complete map component with controls.

    Returns:
        html.Div: Dash component containing the map and its controls.
    """
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

def get_season(date: datetime) -> str:
    """Determine the season based on the date.

    Args:
        date (datetime): Date to analyze.

    Returns:
        str: Name of the season ('Spring', 'Summer', 'Autumn', 'Winter').
    """
    month = date.month
    if month in [3, 4, 5]:
        return 'Printemps'
    elif month in [6, 7, 8]:
        return 'Été'
    elif month in [9, 10, 11]:
        return 'Automne'
    else:
        return 'Hiver'

def generate_map_figure(df: pd.DataFrame, mode: str = "scatter", selected_point: Optional[Dict[Any, Any]] = None) -> go.Figure:
    """Generate a map figure based on the selected visualization mode.

    Args:
        df (pd.DataFrame): DataFrame containing migration data.
        mode (str): Visualization mode ('scatter', 'density', 'trajectory').
        selected_point (Optional[Dict[Any, Any]]): Selected point to highlight.

    Returns:
        go.Figure: Plotly map figure with visualized data.
    """
    season_colors = {
        'Printemps': 'green',
        'Été': 'red',
        'Automne': 'orange',
        'Hiver': 'blue'
    }
    
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['season'] = df['timestamp'].apply(get_season)
    
    if mode == "scatter":
        fig = px.scatter_mapbox(
            df,
            lat="location_lat",
            lon="location_long",
            hover_name="timestamp",
            color='season',
            color_discrete_map=season_colors,
            zoom=3
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
    
    else:  # Trajectory Mode
        df = df.sort_values(['individual_id', 'timestamp'])
        fig = go.Figure()
        
        for individual in df['individual_id'].unique():
            individual_data = df[df['individual_id'] == individual]
            
            valid_lats = []
            valid_lons = []
            
            for i in range(len(individual_data) - 1):
                lat1 = individual_data.iloc[i]['location_lat']
                lon1 = individual_data.iloc[i]['location_long']
                lat2 = individual_data.iloc[i + 1]['location_lat']
                lon2 = individual_data.iloc[i + 1]['location_long']
                
                distance = haversine_distance(lat1, lon1, lat2, lon2)
                
                if i == 0:
                    valid_lats.append(lat1)
                    valid_lons.append(lon1)
                
                if distance <= 300:
                    valid_lats.append(lat2)
                    valid_lons.append(lon2)
                else:
                    if len(valid_lats) > 0:
                        fig.add_trace(go.Scattermapbox(
                            lat=valid_lats,
                            lon=valid_lons,
                            mode='lines',
                            line=dict(width=3, color='blue'),
                            showlegend=False
                        ))
                    valid_lats = [lat2]
                    valid_lons = [lon2]
            
            if len(valid_lats) > 0:
                fig.add_trace(go.Scattermapbox(
                    lat=valid_lats,
                    lon=valid_lons,
                    mode='lines',
                    line=dict(width=3, color='blue'),
                    showlegend=False
                ))
    
    fig.update_layout(
        mapbox_style="open-street-map",
        margin={"l": 0, "r": 0, "t": 0, "b": 0},
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=1.02,
            title="Saisons"
        ),
        mapbox=dict(
            center=dict(lat=df['location_lat'].mean(), lon=df['location_long'].mean()),
            zoom=3
        )
    )
    return fig

@callback(
    Output("map", "figure"),
    [Input("app-state", "data"),
     Input("current-data", "data")],
    prevent_initial_call=True
)
def update_map(app_state: dict, current_data: dict) -> go.Figure:
    """Update the map based on the application's state and current data.

    Args:
        app_state (dict): Application state containing the selected visualization mode.
        current_data (dict): Current migration data to display.

    Returns:
        go.Figure: Updated Plotly map figure.
    """
    if not app_state or not current_data:
        return dash.no_update
    
    df = pd.DataFrame(current_data)
    mode = app_state.get('view_mode', 'scatter') if app_state else 'scatter'
    
    return generate_map_figure(df, mode)
