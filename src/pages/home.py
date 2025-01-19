"""Application Homepage

This page provides an overview of migratory data with key statistics and graphs.

Main Features:
- **Species Selection**: Allows choosing the species to analyze.
- **Statistics**: Displays key indicators:
    - Average distance traveled
    - Average migration duration
    - Average speed
    - Maximum amplitude
- **Interactive Graphs**:
    - Average speed by month
    - Distance traveled by month
"""

from dash import html, dcc, register_page
import dash_bootstrap_components as dbc
from src.components import (
    create_species_select,
    create_stats_cards,
    create_speed_chart,
    create_distance_chart
)

# ----- Registering the page -----
register_page(__name__, path='/')

# ----- Homepage layout -----
def layout() -> html.Div:
    """Create the layout for the homepage.
    
    This function assembles the following components:
    - Stores: Manages the state and data.
    - Page title.
    - Species selector.
    - Statistical cards and interactive charts.
    
    Returns:
        html.Div: Complete structure of the homepage.
    """
    return dbc.Container([
        dcc.Store(id='current-data', storage_type='memory'),  # Stores current data
        dcc.Store(id='app-state', storage_type='memory'),     # Global app state

        dbc.Row([
            dbc.Col(html.H1("Statistiques des Migrations", className="text-center mb-4 mt-4"), width=12),
            dbc.Col(create_species_select(), width=3),  # Species selector
            dbc.Col([
                dbc.Row([
                    dbc.Col(create_stats_cards(), width=5),  # Statistical cards
                    dbc.Col(create_speed_chart(), width=7)   # Speed chart
                ], className="mb-4"),
                dbc.Row([
                    dbc.Col(create_distance_chart(), width=12)  # Distance chart
                ])
            ], width=9)
        ])
    ], fluid=True)