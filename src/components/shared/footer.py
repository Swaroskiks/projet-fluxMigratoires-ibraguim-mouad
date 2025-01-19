"""Footer component for the application."""

from dash import html
import dash_bootstrap_components as dbc

def create_footer() -> html.Div:
    """Creates the footer with credits and a link to the source code."""
    return html.Div([
        html.Hr(),
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.P([
                        "Développé par Ibraguim et Mouad - ",
                        html.A("Code source", 
                                href="https://github.com/Swaroskiks/projet-fluxMigratoires-ibraguim-mouad",
                                className="text-decoration-none"),
                    ], className="text-center text-muted")
                ])
            ])
        ], className="py-3")
    ])