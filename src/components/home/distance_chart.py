"""Distance Chart Component."""

from typing import List
from dash import html, dcc, callback, Input, Output, ALL
import plotly.graph_objects as go
import pandas as pd
from src.utils.data_manager import load_species_data_from_csv, load_species_metadata
from src.components.visualization.map import haversine_distance

def create_distance_chart() -> html.Div:
    """Create the distance chart component."""
    return html.Div([
        dcc.Graph(id='distance-chart')
    ])

def calculate_monthly_distance(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate total distance traveled per month.
    
    Args:
        df (pd.DataFrame): DataFrame with columns ['individual_id', 'timestamp', 'location_lat', 'location_long']
        
    Returns:
        pd.DataFrame: Monthly distances with columns ['month', 'distance']
    """
    df = df.sort_values(['individual_id', 'timestamp'])
    df['month'] = df['timestamp'].dt.month
    monthly_stats = []
    
    for individual in df['individual_id'].unique():
        individual_data = df[df['individual_id'] == individual]
        
        for month in range(1, 13):
            month_data = individual_data[individual_data['month'] == month]
            if len(month_data) < 2:
                continue
                
            monthly_distance: float = 0
            
            # Calcul des distances entre points consécutifs
            for i in range(len(month_data) - 1):
                lat1 = month_data.iloc[i]['location_lat']
                lon1 = month_data.iloc[i]['location_long']
                lat2 = month_data.iloc[i + 1]['location_lat']
                lon2 = month_data.iloc[i + 1]['location_long']
                
                distance = haversine_distance(lat1, lon1, lat2, lon2)
                if distance <= 300:  # Filtre des valeurs aberrantes
                    monthly_distance += distance
            
            if monthly_distance > 0:
                monthly_stats.append({
                    'month': month,
                    'distance': monthly_distance
                })
    
    monthly_df = pd.DataFrame(monthly_stats)
    if not monthly_df.empty:
        return monthly_df.groupby('month')['distance'].sum().reset_index()
    return pd.DataFrame({'month': range(1, 13), 'distance': [0] * 12})

@callback(
    Output('distance-chart', 'figure'),
    [Input({'type': 'species-button', 'index': ALL}, 'color')],
    prevent_initial_call=True
)
def update_distance_chart(colors: List[str]) -> go.Figure:
    """Update distance chart based on species selection."""
    month_names = {
        1: 'Janvier', 2: 'Février', 3: 'Mars', 4: 'Avril',
        5: 'Mai', 6: 'Juin', 7: 'Juillet', 8: 'Août',
        9: 'Septembre', 10: 'Octobre', 11: 'Novembre', 12: 'Décembre'
    }

    fig = go.Figure()
    
    if not colors or 'primary' not in colors:
        months = list(month_names.values())
        empty_values = [0] * len(months)
        fig.add_trace(go.Bar(x=months, y=empty_values))
    else:
        selected_index = colors.index('primary')
        data = load_species_metadata()
        selected_species = data['datasets'][selected_index]['id']
        
        df = load_species_data_from_csv(selected_species)
        monthly_stats = calculate_monthly_distance(df)
        monthly_stats['month_name'] = monthly_stats['month'].map(month_names)
        
        fig.add_trace(go.Bar(
            x=monthly_stats['month_name'],
            y=monthly_stats['distance'].round().astype(int),
            name='Distance'
        ))

    fig.update_layout(
        title="Distance parcourue par mois",
        height=300,
        margin=dict(t=30, b=0, l=0, r=0),
        showlegend=False,
        yaxis_title="Distance (km)"
    )
    
    return fig