"""Migration Data Cleaning and Preprocessing Module.

This module provides functions to prepare raw data from Movebank
by performing cleaning and transformation operations to ensure data quality.

Operations performed:
- Removal of duplicates and handling of missing values.
- Correction of format errors and filtering of outliers.
- Date conversion and GPS coordinate normalization.
- Calculation of speeds and identification of migration periods.
"""

from pathlib import Path
from typing import List, Optional, Union
from config import DATA_RAW_DIR, DATA_CLEANED_DIR
import pandas as pd

def load_raw_data(filepath: Union[str, Path]) -> Optional[pd.DataFrame]:
    """Load raw data from a CSV file.

    Args:
        filepath (Union[str, Path]): Path to the CSV file.

    Returns:
        Optional[pd.DataFrame]: DataFrame containing the data or None if the load failed.
    """
    print(f"[INFO] Chargement des données depuis {filepath}...")
    try:
        return pd.read_csv(filepath)
    except Exception as e:
        print(f"[ERROR] Erreur lors du chargement des données : {str(e)}")
        return None

def select_essential_columns(data: pd.DataFrame, essential_columns: List[str]) -> pd.DataFrame:
    """Select essential columns from the data.

    Args:
        data (pd.DataFrame): DataFrame containing the data.
        essential_columns (List[str]): List of essential columns.

    Returns:
        pd.DataFrame: DataFrame containing only the essential columns.
    """
    available_columns = [col for col in essential_columns if col in data.columns]
    missing_columns = set(essential_columns) - set(available_columns)
    if missing_columns:
        print(f"[WARN] Colonnes manquantes : {missing_columns}")
    return data[available_columns]

def remove_duplicates(data: pd.DataFrame) -> pd.DataFrame:
    """Remove duplicate records from the data.

    Args:
        data (pd.DataFrame): DataFrame containing the data.

    Returns:
        pd.DataFrame: DataFrame without duplicate records.
    """
    initial_rows = len(data)
    data = data.drop_duplicates()
    duplicates_removed = initial_rows - len(data)
    if duplicates_removed > 0:
        print(f"[INFO] {duplicates_removed} doublons supprimés")
    return data

def convert_timestamps(data: pd.DataFrame) -> pd.DataFrame:
    """Convert timestamps to datetime format.

    Args:
        data (pd.DataFrame): DataFrame containing the data.

    Returns:
        pd.DataFrame: DataFrame with timestamps converted to datetime.
    """
    try:
        data['timestamp'] = pd.to_datetime(data['timestamp'])
        print("[INFO] Timestamps convertis avec succès")
    except Exception as e:
        print(f"[WARN] Erreur lors de la conversion des timestamps : {str(e)}")
    return data

def filter_outliers(data: pd.DataFrame) -> pd.DataFrame:
    """Filter outliers from the data.

    Args:
        data (pd.DataFrame): DataFrame containing the data.

    Returns:
        pd.DataFrame: DataFrame without outliers.
    """
    return data[
        (data['location_lat'].between(-90, 90)) &
        (data['location_long'].between(-180, 180))
    ]

def clean_data(data: pd.DataFrame) -> pd.DataFrame:
    """Clean the data by removing duplicates, handling missing values, and filtering outliers.

    Args:
        data (pd.DataFrame): DataFrame containing the data.

    Returns:
        pd.DataFrame: Cleaned DataFrame.
    """
    essential_columns = [
        'individual_id',
        'timestamp',
        'location_long',
        'location_lat',
        'individual_local_identifier',
        'event_id'
    ]
    data = select_essential_columns(data, essential_columns)
    data = remove_duplicates(data)
    data = convert_timestamps(data)
    data = filter_outliers(data)
    return data

def save_cleaned_data(data: pd.DataFrame, output_file: Union[str, Path]) -> None:
    """Save cleaned data to a CSV file.

    Args:
        data (pd.DataFrame): DataFrame containing the cleaned data.
        output_file (Union[str, Path]): Path to the output CSV file.
    """
    try:
        data.to_csv(output_file, index=False)
        print(f"[INFO] Données nettoyées sauvegardées dans {output_file}")
        print(f"[INFO] Nombre d'enregistrements : {len(data)}")
    except Exception as e:
        print(f"[ERROR] Erreur lors de la sauvegarde des données : {str(e)}")

def clean_all_species_data() -> None:
    """Clean and save cleaned data for all species."""
    raw_files = DATA_RAW_DIR.glob("*_raw.csv")
    
    for input_file in raw_files:
        output_file = DATA_CLEANED_DIR / input_file.name.replace("_raw.csv", "_cleaned.csv")
        
        print(f"\n[INFO] Traitement des données pour {input_file.name}...")
        data = load_raw_data(input_file)
        if data is not None and not data.empty:
            cleaned_data = clean_data(data)
            save_cleaned_data(cleaned_data, output_file)
        else:
            print(f"[ERROR] Aucune donnée valide pour {input_file.name}")