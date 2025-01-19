"""Component for visualizing monthly migration distances.

Displays a graph of distances traveled per month to observe
seasonal variations and identify active migration periods.
"""

from typing import List
from dash import html, dcc, callback, Input, Output, ALL
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from src.utils import (
    load_species_data_from_csv, 
    load_species_metadata,
    calculate_monthly_distances
)

def create_distance_chart() -> html.Div:
    """
    Creates the monthly distance chart.
    
    Returns:
        html.Div: Dash component containing the chart.
    """
    return html.Div([
        dbc.Card([
            dbc.CardBody([
                dcc.Graph(
                    id='monthly-distances',
                    config={'displayModeBar': False}
                )
            ])
        ])
    ])

@callback(
    Output('monthly-distances', 'figure'),
    [Input({'type': 'species-button', 'index': ALL}, 'color')]
)
def update_distance_chart(colors: List[str]) -> go.Figure:
    """Update the monthly distance chart based on the selected species.
    
    Args:
        colors (List[str]): List of colors.
    
    Returns:
        go.Figure: Distance chart figure.
    """
    fig = go.Figure()
    
    # Default layout
    fig.update_layout(
        title="Distance parcourue par mois",
        xaxis_title="Mois",
        yaxis_title="Distance (km)",
        showlegend=True,
        template='plotly_white',
        height=400
    )

    if not colors or 'primary' not in colors:
        return fig

    try:
        selected_index = colors.index('primary')
        data = load_species_metadata()
        selected_species = data['datasets'][selected_index]['id']
        df = load_species_data_from_csv(selected_species)
        
        if df.empty:
            return fig
            
        monthly_stats = calculate_monthly_distances(df)
        if monthly_stats.empty:
            return fig
        
        monthly_stats['month_name'] = monthly_stats['month'].dt.strftime('%B')  # Use datetime strftime instead of map
        monthly_stats = monthly_stats.sort_values('month')
        
        # Add trace for each individual
        for individual in monthly_stats['individual'].unique():
            ind_data = monthly_stats[monthly_stats['individual'] == individual]
            fig.add_trace(go.Scatter(
                x=ind_data['month_name'],
                y=ind_data['distance'],
                name=f'Individual {individual}',
                mode='lines+markers'
            ))
            
    except Exception as e:
        print(f"Error updating distance chart: {str(e)}")
        return fig

    return fig