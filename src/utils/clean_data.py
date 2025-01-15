import pandas as pd
import json
from pathlib import Path

# Charge les informations sur les espèces depuis data.json
def load_species_data():
    data_path = "data/data.json"
    with open(data_path, 'r', encoding='utf-8') as file:
        return json.load(file)

# Charge et nettoie les données du fichier CSV en paramètre (son chemin)
def load_data(filepath, species_info=None):
    print(f"[INFO] Chargement des données depuis {filepath}...")

    try:
        # Charger les données
        data = pd.read_csv(filepath)
        
        # Colonnes essentielles à conserver
        essential_columns = [
            'timestamp',
            'location_long',
            'location_lat',
            'individual_local_identifier',
            'study_id',
            'event_id'
        ]
        
        # On vérifie les colonnes disponibles
        available_columns = [col for col in essential_columns if col in data.columns]
        if len(available_columns) < len(essential_columns):
            missing_columns = set(essential_columns) - set(available_columns)
            print(f"[WARN] Colonnes manquantes : {missing_columns}")
        
        # On sélectionne les colonnes pertinentes
        data = data[available_columns]
        
        # On nettoie les données
        data = clean_data(data)
        
        # On ajoute les informations sur l'espèce si disponibles
        if species_info:
            data['species_name'] = species_info['name']
            data['scientific_name'] = species_info['scientific_name']
        
        return data
    
    except Exception as e:
        print(f"[ERROR] Erreur lors du chargement des données : {str(e)}")
        return None

# Supprime doublons et valeurs aberrantes, convertit timestamps
def clean_data(data):
    df = data.copy()
    
    # Pour les doublons
    initial_rows = len(df)
    df = df.drop_duplicates()
    duplicates_removed = initial_rows - len(df)
    if duplicates_removed > 0:
        print(f"[INFO] {duplicates_removed} doublons supprimés")
    
    # Les timestamps
    try:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        print("[INFO] Timestamps convertis avec succès")
    except Exception as e:
        print(f"[WARN] Erreur lors de la conversion des timestamps : {str(e)}")
    
    # Valeurs aberrantes (coordonnées)
    df = df[
        (df['location_lat'].between(-90, 90)) &
        (df['location_long'].between(-180, 180))
    ]
    
    return df

# On clean les données des espèces listées dans data.json
def process_all_species():
    species_data = load_species_data()
    
    processed_dir = Path("data/cleaned")
    processed_dir.mkdir(parents=True, exist_ok=True)
    
    # Pour chaque espèce
    for dataset in species_data['datasets']:
        input_file = dataset['output_file']
        species_name = dataset['scientific_name'].lower().replace(' ', '-')
        output_file = processed_dir / f"{species_name}_cleaned.csv"
        
        print(f"\n[INFO] Traitement des données pour {dataset['name']}...")
        
        # On charge et nettoie les données
        if Path(input_file).exists():
            data = load_data(input_file, dataset)
            if data is not None and not data.empty:
                # Puis on sauvegarde les données
                data.to_csv(output_file, index=False)
                print(f"[INFO] Données nettoyées sauvegardées dans {output_file}")
                print(f"[INFO] Nombre d'enregistrements : {len(data)}")
            else:
                print(f"[ERROR] Aucune donnée valide pour {dataset['name']}")
        else:
            print(f"[ERROR] Fichier introuvable : {input_file}")

if __name__ == "__main__":
    process_all_species()