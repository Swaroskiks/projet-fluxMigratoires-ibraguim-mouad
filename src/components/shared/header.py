from dash import html
import dash_bootstrap_components as dbc

def create_header() -> dbc.NavbarSimple:
    return dbc.NavbarSimple(
        children=[
            dbc.NavItem(dbc.NavLink("Accueil", href="/")),
            dbc.NavItem(dbc.NavLink("Visualisation", href="/visualization")),
        ],
        brand="Flux Migratoires",
        brand_href="/",
        color="primary",
        dark=True,
    )