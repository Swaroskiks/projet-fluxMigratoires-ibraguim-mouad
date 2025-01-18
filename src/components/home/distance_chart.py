from dash import html, dcc, callback, Input, Output, ALL
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
import pandas as pd
from src.utils import (
    load_species_data_from_csv, 
    load_species_metadata,
    calculate_monthly_distances
)

def create_distance_chart():
    """Crée le graphique des distances mensuelles."""
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
def update_distance_chart(colors):
    """Met à jour le graphique des distances mensuelles."""
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
                name='Distance'
            )
        )
        
        fig.update_layout(
            height=300,
            showlegend=False,
            margin=dict(t=30, b=0, l=0, r=0),
            title={
                'text': 'Distance parcourue par mois (km)',
                'x': 0.5,
                'y': 0.95
            },
            yaxis_title="Distance (km)",
            plot_bgcolor='white',
            paper_bgcolor='white'
        )
        
        return fig
    
    selected_index = colors.index('primary')
    data = load_species_metadata()
    selected_species = data['datasets'][selected_index]['id']
    df = load_species_data_from_csv(selected_species)
    
    monthly_stats = calculate_monthly_distances(df)
    if len(monthly_stats) == 0:
        return fig
    
    monthly_stats['month_name'] = monthly_stats['month'].map(month_names)
    monthly_stats = monthly_stats.sort_values('month')
    
    fig.add_trace(
        go.Bar(
            x=monthly_stats['month_name'],
            y=monthly_stats['avg_distance'],
            name='Distance'
        )
    )
    
    fig.update_layout(
        height=300,
        showlegend=False,
        margin=dict(t=30, b=0, l=0, r=0),
        title={
            'text': 'Distance parcourue par mois (km)',
            'x': 0.5,
            'y': 0.95
        },
        yaxis_title="Distance (km)",
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    
    return fig