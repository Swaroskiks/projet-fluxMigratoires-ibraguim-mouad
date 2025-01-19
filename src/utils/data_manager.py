"""Data manager for the migration tracking application.

This module handles loading and processing migration data, providing functions to:
- Load species metadata
- Load migration data by species
- Validate and transform data
- Manage data caching
"""

import pandas as pd
from pathlib import Path
import json
from typing import Dict, Any
from functools import lru_cache
from datetime import datetime
from typing import Union

@lru_cache(maxsize=32)
def load_species_data_from_csv(species_name: str) -> pd.DataFrame:
    """Load migration data for a given species from a CSV file.

    Args:
        species_name (str): Name of the species.

    Returns:
        pd.DataFrame: DataFrame containing the migration data.
    """
    file_path = Path(__file__).parent.parent.parent / 'data' / 'cleaned' / f'{species_name}_cleaned.csv'
    
    if not file_path.exists():
        raise FileNotFoundError(f"Le fichier {file_path} n'existe pas.")
    
    df = pd.read_csv(file_path)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df

@lru_cache(maxsize=1)
def load_species_metadata() -> Dict[str, Any]:
    """Load species metadata from a JSON file.

    Returns:
        Dict[str, Any]: Dictionary containing species metadata.
    """
    metadata_file = Path(__file__).parent.parent.parent / 'data' / 'species_metadata.json'
    
    if not metadata_file.exists():
        raise FileNotFoundError(f"Le fichier {metadata_file} n'existe pas.")
    
    with open(metadata_file, 'r', encoding='utf-8') as f:
        return json.load(f)

@lru_cache(maxsize=None)
def get_season(date: Union[str, datetime]) -> str:
    """Determine the season based on the date.    
    
    Args:
        date (Union[str, datetime]): Date to analyze.

    Returns:
        str: Name of the season ('Spring', 'Summer', 'Autumn', 'Winter').
    """
    month = pd.to_datetime(date).month
    if month in [3, 4, 5]:
        return 'Printemps'
    elif month in [6, 7, 8]:
        return 'Été'
    elif month in [9, 10, 11]:
        return 'Automne'
    else:
        return 'Hiver'