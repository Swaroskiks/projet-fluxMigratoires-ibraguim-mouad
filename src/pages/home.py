from dash import html, register_page, callback, Input, Output, ALL
import dash_bootstrap_components as dbc
from src.components.species_select import create_species_select
from src.components.distance_histogram import create_distance_histogram
from src.utils.data_manager import load_species_data_from_csv, load_species_metadata
from src.components.map import haversine_distance

register_page(__name__, path='/')

def layout():
    return html.Div([
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    create_species_select()
                ], width=3),
                dbc.Col([
                    html.H1("Suivi des flux migratoires", className="text-center mt-4 mb-4"),
                    html.P("Visualisation et analyse des mouvements migratoires.", className="text-center mb-4"),
                    dbc.Row([
                        dbc.Col([
                            dbc.Card([
                                dbc.CardBody([
                                    html.H4("Statistiques", className="card-title"),
                                    dbc.Row([
                                        dbc.Col([
                                            dbc.Card([
                                                dbc.CardBody([
                                                    html.H3(html.Span(id="total-distance", children="0"), className="text-center"),
                                                    html.P([
                                                        "Distance (km)",
                                                        html.Sup("1")
                                                    ], className="text-center text-muted")
                                                ])
                                            ], color="light")
                                        ]),
                                        dbc.Col([
                                            dbc.Card([
                                                dbc.CardBody([
                                                    html.H3(html.Span(id="avg-speed", children="0"), className="text-center"),
                                                    html.P([
                                                        "Vitesse (km/h)",
                                                        html.Sup("2")
                                                    ], className="text-center text-muted")
                                                ])
                                            ], color="light")
                                        ])
                                    ], className="mb-3"),
                                    dbc.Row([
                                        dbc.Col([
                                            dbc.Card([
                                                dbc.CardBody([
                                                    html.H3(html.Span(id="max-distance", children="0"), className="text-center"),
                                                    html.P([
                                                        "Amplitude (km)",
                                                        html.Sup("3")
                                                    ], className="text-center text-muted")
                                                ])
                                            ], color="light")
                                        ]),
                                        dbc.Col([
                                            dbc.Card([
                                                dbc.CardBody([
                                                    html.H3(html.Span(id="duration", children="0"), className="text-center"),
                                                    html.P([
                                                        "Durée de suivi",
                                                        html.Sup("4")
                                                    ], className="text-center text-muted")
                                                ])
                                            ], color="light")
                                        ])
                                    ]),
                                    html.Div([
                                        html.P([
                                            html.Sup("1"), " Distance totale parcourue par l'espèce"
                                        ], className="mb-1 small text-muted"),
                                        html.P([
                                            html.Sup("2"), " Vitesse moyenne de déplacement"
                                        ], className="mb-1 small text-muted"),
                                        html.P([
                                            html.Sup("3"), " Distance maximale entre deux points"
                                        ], className="mb-1 small text-muted"),
                                        html.P([
                                            html.Sup("4"), " Nombre de jours de suivi"
                                        ], className="mb-1 small text-muted")
                                    ], className="mt-3")
                                ])
                            ], className="mb-4")
                        ], width=5),
                        dbc.Col([
                            dbc.Card([
                                dbc.CardBody([
                                    create_distance_histogram()
                                ])
                            ])
                        ], width=5)
                    ])
                ], width=9)
            ])
        ], className="py-4", fluid=True)
    ])

@callback(
    [Output("total-distance", "children"),
     Output("avg-speed", "children"),
     Output("max-distance", "children"),
     Output("duration", "children")],
    [Input({'type': 'species-button', 'index': ALL}, 'color')]
)
def update_stats(colors):
    if not colors or 'primary' not in colors:
        return "0", "0", "0", "0"
    
    selected_index = colors.index('primary')
    data = load_species_metadata()
    selected_species = data['datasets'][selected_index]['id']
    
    df = load_species_data_from_csv(selected_species)
    print(f"Loaded data shape: {df.shape}")
    
    total_distance = 0
    total_speed = 0
    speed_count = 0
    
    for individual in df['individual_id'].unique():
        ind_data = df[df['individual_id'] == individual].sort_values('timestamp')
        for i in range(len(ind_data) - 1):
            lat1 = ind_data.iloc[i]['location_lat']
            lon1 = ind_data.iloc[i]['location_long']
            lat2 = ind_data.iloc[i + 1]['location_lat']
            lon2 = ind_data.iloc[i + 1]['location_long']
            time1 = ind_data.iloc[i]['timestamp']
            time2 = ind_data.iloc[i + 1]['timestamp']
            
            distance = haversine_distance(lat1, lon1, lat2, lon2)
            time_diff = (time2 - time1).total_seconds() / 3600
            
            if distance <= 300 and time_diff > 0:
                total_distance += distance
                speed = distance / time_diff
                total_speed += speed
                speed_count += 1
    
    print(f"Total distance: {total_distance}")
    print(f"Speed count: {speed_count}")
    
    avg_speed = int(total_speed / speed_count) if speed_count > 0 else 0
    
    # Calcul rapide de l'amplitude en utilisant les points extrêmes
    lat_min_idx = df['location_lat'].idxmin()
    lat_max_idx = df['location_lat'].idxmax()
    lon_min_idx = df['location_long'].idxmin()
    lon_max_idx = df['location_long'].idxmax()
    
    # Points extrêmes
    points = [
        (df.loc[lat_min_idx, 'location_lat'], df.loc[lat_min_idx, 'location_long']),
        (df.loc[lat_max_idx, 'location_lat'], df.loc[lat_max_idx, 'location_long']),
        (df.loc[lon_min_idx, 'location_lat'], df.loc[lon_min_idx, 'location_long']),
        (df.loc[lon_max_idx, 'location_lat'], df.loc[lon_max_idx, 'location_long'])
    ]
    
    # Calcul des distances entre les points extrêmes
    max_distance = 0
    for i in range(len(points)):
        for j in range(i + 1, len(points)):
            lat1, lon1 = points[i]
            lat2, lon2 = points[j]
            distance = int(haversine_distance(lat1, lon1, lat2, lon2))
            max_distance = max(max_distance, distance)
    
    duration = (df['timestamp'].max() - df['timestamp'].min()).days
    
    return (
        f"{int(total_distance):,}",
        f"{avg_speed}",
        f"{max_distance}",
        f"{duration}"
    )