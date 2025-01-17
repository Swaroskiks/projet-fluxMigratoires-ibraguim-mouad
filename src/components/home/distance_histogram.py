from dash import html, dcc, callback, Input, Output, ALL
import plotly.express as px
import pandas as pd
from src.utils import load_species_data_from_csv, load_species_metadata
from src.components import haversine_distance
import dash
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def calculate_monthly_stats(df):
    df = df.sort_values(['individual_id', 'timestamp'])
    df['month'] = df['timestamp'].dt.month
    monthly_stats = []
    
    for individual in df['individual_id'].unique():
        individual_data = df[df['individual_id'] == individual]
        
        for month in range(1, 13):
            month_data = individual_data[individual_data['month'] == month]
            if len(month_data) < 2:
                continue
                
            speeds = []
            monthly_distance = 0
            
            for i in range(len(month_data) - 1):
                lat1 = month_data.iloc[i]['location_lat']
                lon1 = month_data.iloc[i]['location_long']
                lat2 = month_data.iloc[i + 1]['location_lat']
                lon2 = month_data.iloc[i + 1]['location_long']
                time1 = month_data.iloc[i]['timestamp']
                time2 = month_data.iloc[i + 1]['timestamp']
                
                distance = haversine_distance(lat1, lon1, lat2, lon2)
                time_diff = (time2 - time1).total_seconds() / 3600
                
                if distance <= 300 and time_diff > 0:
                    speed = distance / time_diff
                    speeds.append(speed)
                    monthly_distance += distance
            
            if speeds:
                monthly_stats.append({
                    'month': month,
                    'speed': sum(speeds) / len(speeds),
                    'distance': monthly_distance
                })
    
    monthly_df = pd.DataFrame(monthly_stats)
    return monthly_df.groupby('month').agg({
        'speed': 'mean',
        'distance': 'sum'
    }).reset_index()

def create_distance_histogram():
    return html.Div([
        dcc.Graph(id='movement-stats')
    ])

@callback(
    Output('movement-stats', 'figure'),
    [Input({'type': 'species-button', 'index': ALL}, 'color')],
    prevent_initial_call=True
)
def update_stats(colors):
    month_names = {
        1: 'Janvier', 2: 'Février', 3: 'Mars', 4: 'Avril',
        5: 'Mai', 6: 'Juin', 7: 'Juillet', 8: 'Août',
        9: 'Septembre', 10: 'Octobre', 11: 'Novembre', 12: 'Décembre'
    }

    fig = make_subplots(rows=2, cols=1, subplot_titles=('Vitesse moyenne par mois (km/h)', 'Distance parcourue par mois (km)'))
    
    if not colors or 'primary' not in colors:
        months = list(month_names.values())
        empty_values = [0] * len(months)
        
        fig.add_trace(
            go.Bar(
                x=months,
                y=empty_values,
                name='Vitesse'
            ),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Bar(
                x=months,
                y=empty_values,
                name='Distance'
            ),
            row=2, col=1
        )
        
        fig.update_layout(
            height=600,
            showlegend=False,
            margin=dict(t=30, b=0, l=0, r=0)
        )
        
        fig.update_yaxes(title_text="Vitesse (km/h)", row=1, col=1)
        fig.update_yaxes(title_text="Distance (km)", row=2, col=1)
        
        return fig
    
    selected_index = colors.index('primary')
    data = load_species_metadata()
    selected_species = data['datasets'][selected_index]['id']
    
    df = load_species_data_from_csv(selected_species)
    monthly_stats = calculate_monthly_stats(df)
    monthly_stats['month_name'] = monthly_stats['month'].map(month_names)
    
    fig.add_trace(
        go.Bar(
            x=monthly_stats['month_name'],
            y=monthly_stats['speed'],
            name='Vitesse'
        ),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Bar(
            x=monthly_stats['month_name'],
            y=monthly_stats['distance'],
            name='Distance'
        ),
        row=2, col=1
    )

    fig.update_layout(
        height=600,
        showlegend=False,
        margin=dict(t=30, b=0, l=0, r=0)
    )
    
    fig.update_yaxes(title_text="Vitesse (km/h)", row=1, col=1)
    fig.update_yaxes(title_text="Distance (km)", row=2, col=1)
    
    return fig
