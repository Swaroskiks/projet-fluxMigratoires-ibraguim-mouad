from dash import html, dcc, register_page
import dash_bootstrap_components as dbc
from src.components import (
    create_species_select,
    create_stats_cards,
    create_speed_chart,
    create_distance_chart
)

register_page(__name__, path='/')

def layout():
    return html.Div([
        dcc.Store(id='current-data', storage_type='memory'),
        dcc.Store(id='app-state', storage_type='memory'),

        dbc.Container([
            dbc.Row([
                dbc.Col(
                    html.H1("Statistiques", className="text-center mb-4 mt-4"),
                    width=12
                ),

                dbc.Col(
                    create_species_select(),
                    width=3
                ),
                
                dbc.Col([
                    dbc.Row([
                        dbc.Col([
                            create_stats_cards()
                        ], width=5),
                        
                        dbc.Col([
                            create_speed_chart()
                        ], width=7)
                    ], className="mb-4"),
                    
                    dbc.Row([
                        dbc.Col([
                            create_distance_chart()
                        ], width=12)
                    ])
                ], width=9)
            ])
        ], fluid=True)
    ])