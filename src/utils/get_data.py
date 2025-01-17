import os
from dotenv import load_dotenv
from config import MOVEBANK_BASE_URL, MOVEBANK_USERNAME, MOVEBANK_PASSWORD, DATA_RAW_DIR
import requests
import hashlib
from src.utils.data_manager import load_species_metadata

def download_movebank_data(movebank_id, output_file):
    session = requests.Session()
    
    params = {
        "entity_type": "event",
        "study_id": movebank_id,
        "attributes": "all"
    }
    
    # Première requête pour récupérer les termes de licence
    response = session.get(MOVEBANK_BASE_URL, params=params, auth=(MOVEBANK_USERNAME, MOVEBANK_PASSWORD))
    
    if "License Terms:" in response.text:
        print("[INFO] Acceptation des termes de la licence...")

        # Calcul du hash MD5 du contenu de la licence
        license_content = response.text.encode('utf-8')
        md5_hash = hashlib.md5(license_content).hexdigest()
        print(f"[DEBUG] Hash MD5 généré : {md5_hash}")

        # Nouvelle requête avec le hash MD5
        params["license-md5"] = md5_hash
        response = session.get(MOVEBANK_BASE_URL, params=params, auth=(MOVEBANK_USERNAME, MOVEBANK_PASSWORD))

    # Vérification et sauvegarde
    if response.status_code == 200 and not response.text.startswith("<html>"):
        with open(output_file, "wb") as file:
            file.write(response.content)
        print(f"[INFO] Données téléchargées dans '{output_file}'")
        return True
    else:
        print(f"[ERROR] Échec du téléchargement : {response.status_code}")
        print("[DEBUG] Contenu de la réponse :", response.text[:500])
        return False

def download_all_species_data():
    species_metadata = load_species_metadata()
    success_count = 0
    total_count = len(species_metadata['datasets'])

    for dataset in species_metadata['datasets']:
        movebank_id = dataset['movebank_id']
        output_file = os.path.join(DATA_RAW_DIR, f"{dataset['id']}_raw.csv")
        
        print(f"\n[INFO] Téléchargement des données pour {dataset['name']} (ID: {movebank_id})")
        if download_movebank_data(movebank_id, output_file):
            success_count += 1

    print(f"\n[INFO] Téléchargement terminé : {success_count}/{total_count} études téléchargées avec succès")