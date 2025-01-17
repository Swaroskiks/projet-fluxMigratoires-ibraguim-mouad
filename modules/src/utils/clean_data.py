from config import DATA_RAW_DIR, DATA_CLEANED_DIR
import pandas as pd
from pathlib import Path

def load_raw_data(filepath):
    print(f"[INFO] Chargement des données depuis {filepath}...")
    try:
        return pd.read_csv(filepath)
    except Exception as e:
        print(f"[ERROR] Erreur lors du chargement des données : {str(e)}")
        return None

def select_essential_columns(data, essential_columns):
    available_columns = [col for col in essential_columns if col in data.columns]
    missing_columns = set(essential_columns) - set(available_columns)
    if missing_columns:
        print(f"[WARN] Colonnes manquantes : {missing_columns}")
    return data[available_columns]

def remove_duplicates(data):
    initial_rows = len(data)
    data = data.drop_duplicates()
    duplicates_removed = initial_rows - len(data)
    if duplicates_removed > 0:
        print(f"[INFO] {duplicates_removed} doublons supprimés")
    return data

def convert_timestamps(data):
    try:
        data['timestamp'] = pd.to_datetime(data['timestamp'])
        print("[INFO] Timestamps convertis avec succès")
    except Exception as e:
        print(f"[WARN] Erreur lors de la conversion des timestamps : {str(e)}")
    return data

def filter_outliers(data):
    return data[
        (data['location_lat'].between(-90, 90)) &
        (data['location_long'].between(-180, 180))
    ]

def clean_data(data):
    essential_columns = [
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

def save_cleaned_data(data, output_file):
    try:
        data.to_csv(output_file, index=False)
        print(f"[INFO] Données nettoyées sauvegardées dans {output_file}")
        print(f"[INFO] Nombre d'enregistrements : {len(data)}")
    except Exception as e:
        print(f"[ERROR] Erreur lors de la sauvegarde des données : {str(e)}")

def clean_all_species_data():
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