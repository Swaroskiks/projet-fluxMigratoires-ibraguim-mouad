import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px

# Chemin vers le fichier CSV contenant les données GPS
csv_file_path = "../../data/cleaned/corrected_data.csv"

# Charger les données depuis le fichier CSV
try:
    df = pd.read_csv(csv_file_path)

    # Vérifier si les colonnes nécessaires sont présentes
    required_columns = ["timestamp", "location-long", "location-lat", "event-id"]
    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"La colonne '{col}' est absente dans le fichier CSV.")

    # Convertir la colonne 'timestamp' en format datetime pour une meilleure gestion des dates
    df["timestamp"] = pd.to_datetime(df["timestamp"])

except Exception as e:
    print(f"[ERROR] Problème lors du chargement des données : {e}")
    exit()

# Initialisation de l'application Dash
app = dash.Dash(__name__)

# Mise en page du Dashboard
app.layout = html.Div(
    style={"textAlign": "center", "fontFamily": "Arial"},
    children=[
        html.H1("Carte GPS - Dashboard", style={"marginBottom": "20px"}),
        html.Div(
            dcc.RadioItems(
                id="map-mode",
                options=[
                    {"label": "Affichage des points", "value": "scatter"},
                    {"label": "Carte de densité", "value": "density"},
                    {"label": "Trajectoire Moyenne", "value": "trajectory"},
                ],
                value="scatter",
                labelStyle={"display": "inline-block", "marginRight": "10px"},
                style={"marginBottom": "20px"},
            ),
        ),
        html.Div(
            dcc.Graph(id="map"),
            style={
                "display": "inline-block",
                "borderRadius": "20px",  # Arrondir les bords
                "overflow": "hidden",   # Masquer le contenu débordant
                "boxShadow": "0 4px 8px rgba(0, 0, 0, 0.2)",  # Ajouter une ombre
            },
        ),
        html.Div(
            id="slider-container",
            style={
                "marginTop": "20px",
                "width": "756px",  # Correspond à la largeur de la carte
                "marginLeft": "auto",
                "marginRight": "auto",
            },
            children=[
                dcc.Slider(
                    id="time-slider",
                    min=0,
                    max=len(df) - 1,
                    step=1,
                    value=0,
                    marks={
                        i: str(df["timestamp"].iloc[i].date())
                        for i in range(0, len(df), len(df) // 10)  # Espacement des marques
                    },
                )
            ],
        ),
    ],
)


@app.callback(
    Output("map", "figure"),
    [Input("map-mode", "value"), Input("time-slider", "value")]
)
def update_map(map_mode, slider_index):
    # Point sélectionné en fonction du slider
    selected_point = df.iloc[slider_index] if map_mode == "scatter" else None

    if map_mode == "scatter":
        # Carte classique avec des points GPS
        fig = px.scatter_mapbox(
            df,
            lat="location-lat",
            lon="location-long",
            hover_name="timestamp",
            hover_data={"event-id": True},
            zoom=3,  # Niveau de zoom
            title="Trajectoires GPS",
        )

        # Mettre en évidence le point sélectionné
        if selected_point is not None:
            fig.add_scattermapbox(
                lat=[selected_point["location-lat"]],
                lon=[selected_point["location-long"]],
                mode="markers+text",
                marker=dict(
                    size=15,  # Point plus grand
                    color="yellow",  # Couleur jaune
                    opacity=1,
                    symbol="circle",
                ),
                text=["Point sélectionné"],  # Le texte au-dessus du point
                hovertext=[
                    f"Date : <b>{selected_point['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}</b>"
                ],
                hovertemplate="<b style='background-color:white; color:black; padding:5px; border-radius:10px;'>%{hovertext}</b><extra></extra>",
                name="Point sélectionné",
            )

    elif map_mode == "density":
        # Carte de densité des données GPS
        fig = px.density_mapbox(
            df,
            lat="location-lat",
            lon="location-long",
            z=None,  # Pas de valeur z pour afficher uniquement la densité
            radius=10,  # Taille du rayon pour la densité
            title="Densité des trajectoires GPS",
            zoom=3,  # Niveau de zoom
        )
    elif map_mode == "trajectory":
        # Calculer la trajectoire moyenne
        grouped = df.groupby(df.index // 20).agg({
            "location-lat": "mean",
            "location-long": "mean",
            "timestamp": "first"  # Conserver un timestamp représentatif
        }).reset_index(drop=True)
        fig = px.line_mapbox(
            grouped,
            lat="location-lat",
            lon="location-long",
            title="Trajectoire Moyenne GPS",
            zoom=3,  # Niveau de zoom
        )

    fig.update_layout(
        mapbox_style="open-street-map",  # Style de la carte
        height=604,  # Hauteur de la carte en pixels
        width=756,  # Largeur de la carte en pixels
        margin={"l": 0, "r": 0, "t": 50, "b": 0},  # Marges pour centrer
    )
    return fig


# Exécution de l'application
if __name__ == "__main__":
    app.run_server(debug=True)
