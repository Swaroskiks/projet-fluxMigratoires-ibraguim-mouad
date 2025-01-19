"""Component to display key statistics in the form of cards.

Displayed metrics:
- Average migration distance
- Average migration duration
- Average migration speed
- Maximum migration amplitude
"""

from typing import List, Union, Optional
import pandas as pd
from dash import html, callback, Input, Output, ALL
import dash_bootstrap_components as dbc
from src.utils import (
    load_species_data_from_csv,
    load_species_metadata,
    calculate_migration_stats,
    calculate_average_speed,
    calculate_max_amplitude
)

def create_stat_card(title: str, value: Union[int, float, str], unit: str = "") -> dbc.Card:
    """Create a statistical card displaying a title, value, and unit.
    
    Args:
        title (str): The title of the card.
        value (Union[int, float, str]): The value to display.
        unit (str, optional): The unit of the value. Defaults to "".
    
    Returns:
        dbc.Card: The statistical card.
    """
    return dbc.Card(
        dbc.CardBody([
            html.H6(title, className="card-subtitle text-muted"),
            html.H4(
                [str(value), html.Small(f" {unit}")],
                className="card-title"
            )
        ]),
        className="mb-4 text-center shadow-sm"
    )

def create_stats_cards(species_data: Optional[pd.DataFrame] = None) -> html.Div:
    """Create a container with all statistical cards.
    
    Args:
        species_data (Optional[pd.DataFrame], optional): Species data. Defaults to None.
    
    Returns:
        html.Div: Container with all statistical cards.
    """
    return html.Div(
        id="stats-cards",
        children=_generate_stats_cards(species_data)
    )

def _generate_stats_cards(species_data: Optional[pd.DataFrame] = None) -> List[dbc.Card]:
    """Generate the content for the statistical cards.
    
    Args:
        species_data (Optional[pd.DataFrame], optional): Species data. Defaults to None.
    
    Returns:
        List[dbc.Card]: List of statistical cards.
    """
    if not species_data:
        return [
            create_stat_card("Distance moyenne parcourue", 0, "km"),
            create_stat_card("Durée de l'étude", 0, "jours"),
            create_stat_card("Vitesse moyenne", 0, "km/h"),
            create_stat_card("Amplitude maximale", 0, "km")
        ]
    
    df = load_species_data_from_csv(species_data['id'])
    
    avg_distance, avg_duration = calculate_migration_stats(df)
    avg_speed = calculate_average_speed(df)
    max_amplitude = calculate_max_amplitude(df)
    
    return [
        create_stat_card("Distance moyenne de migration", avg_distance, "km"),
        create_stat_card("Durée moyenne de migration", avg_duration, "jours"),
        create_stat_card("Vitesse moyenne", avg_speed, "km/h"),
        create_stat_card("Amplitude maximale", max_amplitude, "km")
    ]

@callback(
    Output("stats-cards", "children"),
    [Input({'type': 'species-button', 'index': ALL}, 'color')]
)
def update_stats(colors: List[str]) -> List[dbc.Card]:
    """Update the statistical cards based on the selected species.
    
    Args:
        colors (List[str]): List of colors.
    
    Returns:
        List[dbc.Card]: List of statistical cards.
    """
    if not colors or 'primary' not in colors:
        return _generate_stats_cards(None)
    
    selected_index = colors.index('primary')
    data = load_species_metadata()
    selected_species = data['datasets'][selected_index]['id']
    
    return _generate_stats_cards({'id': selected_species})
