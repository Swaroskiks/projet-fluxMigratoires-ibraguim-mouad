import dash_bootstrap_components as dbc

navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Accueil", href="#")),
        dbc.NavItem(dbc.NavLink("Visualisation", href="#")),
    ],
    brand="Flux Migratoires des Espèces",
    brand_href="#",
    color="primary",
    dark=True,
)