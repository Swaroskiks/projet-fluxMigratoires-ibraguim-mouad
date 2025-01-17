from functools import lru_cache
from pathlib import Path
import pandas as pd
import json
from typing import Dict, Any

@lru_cache(maxsize=32)
def load_species_data_from_csv(species_name: str) -> pd.DataFrame:
    file_path = Path(f"data/cleaned/{species_name}_cleaned.csv")
    df = pd.read_csv(file_path)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df

@lru_cache(maxsize=1)
def load_species_metadata() -> Dict[str, Any]:
    with open(Path("data/data.json"), 'r', encoding='utf-8') as f:
        return json.load(f)