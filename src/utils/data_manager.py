import pandas as pd
from pathlib import Path
import json
from typing import Dict, Any
from functools import lru_cache

@lru_cache(maxsize=32)
def load_species_data_from_csv(species_name: str) -> pd.DataFrame:
    file_path = Path(__file__).parent.parent.parent / 'data' / 'cleaned' / f'{species_name}_cleaned.csv'
    
    if not file_path.exists():
        raise FileNotFoundError(f"Le fichier {file_path} n'existe pas.")
    
    df = pd.read_csv(file_path)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df

@lru_cache(maxsize=1)
def load_species_metadata() -> Dict[str, Any]:
    metadata_file = Path(__file__).parent.parent.parent / 'data' / 'data.json'
    
    if not metadata_file.exists():
        raise FileNotFoundError(f"Le fichier {metadata_file} n'existe pas.")
    
    with open(metadata_file, 'r', encoding='utf-8') as f:
        return json.load(f)

@lru_cache(maxsize=None)
def get_season(date) -> str:
    month = pd.to_datetime(date).month
    if month in [3, 4, 5]:
        return 'Printemps'
    elif month in [6, 7, 8]:
        return 'Été'
    elif month in [9, 10, 11]:
        return 'Automne'
    else:
        return 'Hiver'