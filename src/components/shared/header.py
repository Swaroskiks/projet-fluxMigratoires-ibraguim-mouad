"""Header component for the application."""

import dash_bootstrap_components as dbc

def create_header() -> dbc.NavbarSimple:
    """Creates the application header with navigation between pages."""
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