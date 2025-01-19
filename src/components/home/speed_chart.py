"""Component for visualizing monthly migration speeds.

Displays an interactive graph showing the average migration speed per month,
helping to identify seasonal trends and peak migration periods.
"""

from typing import List
from dash import html, dcc, callback, Input, Output, ALL
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
import pandas as pd
from src.utils import (
    load_species_data_from_csv, 
    load_species_metadata,
    haversine_distance
)

def create_speed_chart() -> html.Div:
    """Create the monthly average speed chart.

    Returns:
        html.Div: Dash component containing the chart.
    """
    return html.Div([
        dbc.Card([
            dbc.CardBody([
                dcc.Graph(
                    id='monthly-speeds',
                    config={'displayModeBar': False}
                )
            ])
        ])
    ])

@callback(
    Output('monthly-speeds', 'figure'),
    [Input({'type': 'species-button', 'index': ALL}, 'color')]
)
def update_speed_chart(colors: List[str]) -> go.Figure:
    """Update the speed chart based on the selected species.
    
    Args:
        colors (List[str]): List of colors.
    
    Returns:
        go.Figure: Updated speed chart.
    """
    month_names = {
        1: 'Janvier', 2: 'Février', 3: 'Mars', 4: 'Avril',
        5: 'Mai', 6: 'Juin', 7: 'Juillet', 8: 'Août',
        9: 'Septembre', 10: 'Octobre', 11: 'Novembre', 12: 'Décembre'
    }
    
    fig = go.Figure()
    
    if not colors or 'primary' not in colors:
        months = list(month_names.values())
        empty_values = [0] * len(months)
        
        fig.add_trace(
            go.Bar(
                x=months,
                y=empty_values,
                name='Vitesse'
            )
        )
        
        fig.update_layout(
            height=300,
            showlegend=False,
            margin=dict(t=30, b=0, l=0, r=0),
            title={
                'text': 'Vitesse moyenne par mois (km/h)',
                'x': 0.5,
                'y': 0.95
            },
            yaxis_title="Vitesse (km/h)",
            plot_bgcolor='white',
            paper_bgcolor='white'
        )
        
        return fig
    
    selected_index = colors.index('primary')
    data = load_species_metadata()
    selected_species = data['datasets'][selected_index]['id']
    df = load_species_data_from_csv(selected_species)
    
    # Calculer les vitesses moyennes par mois
    monthly_speeds = []
    df['month'] = df['timestamp'].dt.month
    
    for individual in df['individual_id'].unique():
        ind_data = df[df['individual_id'] == individual].sort_values('timestamp')
        for month in range(1, 13):
            month_data = ind_data[ind_data['month'] == month].copy()
            if len(month_data) < 2:
                continue
            
            total_speed = 0
            speed_count = 0
            
            for i in range(len(month_data) - 1):
                lat1, lon1 = month_data.iloc[i]['location_lat'], month_data.iloc[i]['location_long']
                lat2, lon2 = month_data.iloc[i + 1]['location_lat'], month_data.iloc[i + 1]['location_long']
                time1, time2 = month_data.iloc[i]['timestamp'], month_data.iloc[i + 1]['timestamp']
                
                distance = haversine_distance(lat1, lon1, lat2, lon2)
                time_diff = (time2 - time1).total_seconds() / 3600
                
                if distance <= 300 and time_diff > 0:
                    speed = distance / time_diff
                    total_speed += speed
                    speed_count += 1
            
            if speed_count > 0:
                monthly_speeds.append({
                    'month': month,
                    'speed': total_speed / speed_count
                })
    
    if not monthly_speeds:
        return fig
    
    df_speeds = pd.DataFrame(monthly_speeds)
    monthly_avg_speeds = df_speeds.groupby('month')['speed'].mean().reset_index()
    monthly_avg_speeds['month_name'] = monthly_avg_speeds['month'].map(month_names)
    monthly_avg_speeds = monthly_avg_speeds.sort_values('month')
    
    fig.add_trace(
        go.Bar(
            x=monthly_avg_speeds['month_name'],
            y=monthly_avg_speeds['speed'],
            name='Vitesse'
        )
    )
    
    fig.update_layout(
        height=300,
        showlegend=False,
        margin=dict(t=30, b=0, l=0, r=0),
        title={
            'text': 'Vitesse moyenne par mois (km/h)',
            'x': 0.5,
            'y': 0.95
        },
        yaxis_title="Vitesse (km/h)",
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    
    return fig