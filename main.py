# Fichier principal permettant de lancer le dashboard
from dash import Dash
import dash_bootstrap_components as dbc

# Initialisation de l'application Dash
app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    assets_folder='assets'
)

# Titre de l'application
app.title = "Visualisation des Flux Migratoires"

# Mise en page principale
# app.layout = 

# Point d'entrée de l'application
if __name__ == '__main__':
    app.run_server(debug=True, port=8050)