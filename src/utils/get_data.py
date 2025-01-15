import requests
import json
import os
from pathlib import Path
import hashlib

# Informations d'identification
username = "MouadM"
password = "gyzgij4kovcugirsuQ$&"

# URL pour l'API Movebank
url = f"https://www.movebank.org/movebank/service/direct-read"

# Charge les informations sur les espèces depuis data.json
def load_species_data():
    data_path = "data/data.json"
    with open(data_path, 'r', encoding='utf-8') as file:
        return json.load(file)

# Fonction pour télécharger les données d'une étude via son ID
def download_movebank_data(movebank_id, output_file):
    session = requests.Session()
    
    params = {
        "entity_type": "event",
        "study_id": movebank_id,
        "attributes": "all"
    }
    
    # Première requête pour récupérer les termes de licence
    response = session.get(url, params=params, auth=(username, password))
    
    if "License Terms:" in response.text:
        print("[INFO] Acceptation des termes de la licence...")

        # Calcul du hash MD5 du contenu de la licence
        license_content = response.text.encode('utf-8')
        md5_hash = hashlib.md5(license_content).hexdigest()
        print(f"[DEBUG] Hash MD5 généré : {md5_hash}")

        # Nouvelle requête avec le hash MD5
        params["license-md5"] = md5_hash
        response = session.get(url, params=params, auth=(username, password))

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

# Lecture du fichier data.json pour télécharger les données de toutes les espèces 
def download_all_species_data():
    data = load_species_data()
    success_count = 0
    total_count = len(data['datasets'])

    for dataset in data['datasets']:
        movebank_id = dataset['movebank_id']
        output_file = dataset['output_file']
        
        print(f"\n[INFO] Téléchargement des données pour {dataset['name']} (ID: {movebank_id})")
        if download_movebank_data(movebank_id, str(output_file)):
            success_count += 1

    print(f"\n[INFO] Téléchargement terminé : {success_count}/{total_count} études téléchargées avec succès")

if __name__ == "__main__":
    download_all_species_data()
