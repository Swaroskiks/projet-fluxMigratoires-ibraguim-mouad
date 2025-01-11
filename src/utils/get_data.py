import requests

# Informations d'identification
username = "MouadM"
password = "gyzgij4kovcugirsuQ$&"
study_id = "128184877"  # ID de l'étude
output_file = "../../data/raw/movebank_data.csv"  # Nom du fichier CSV de sortie

# URL pour l'API Movebank
url = f"https://www.movebank.org/movebank/service/direct-read"

# Fonction pour télécharger les données
def download_movebank_data():
    # Crée la requête avec l'ID de l'étude
    params = {
        "entity_type": "event",  # Type d'entité (événements de mouvement)
        "study_id": study_id,   # ID de l'étude
        "attributes": "all"     # Télécharger tous les attributs disponibles
    }

    # Effectue la requête GET avec authentification
    response = requests.get(url, params=params, auth=(username, password))

    # Vérifie la réponse pour accepter les termes de la licence
    if "License Terms:" in response.text:
        print("[INFO] Acceptation des termes de la licence...")
        license_md5 = response.text.split("md5=")[-1].split("&")[0]
        params["license-md5"] = license_md5
        response = requests.get(url, params=params, auth=(username, password))

    # Sauvegarde les données si la requête a réussi
    if response.status_code == 200:
        with open(output_file, "wb") as file:
            file.write(response.content)
        print(f"[INFO] Les données ont été téléchargées avec succès dans '{output_file}'")
    else:
        print(f"[ERROR] Échec du téléchargement : {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    download_movebank_data()
