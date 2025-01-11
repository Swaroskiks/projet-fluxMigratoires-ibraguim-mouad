import pandas as pd
import geopandas as gpd
from shapely.geometry import Point


def load_data(filepath, columns_to_keep=None, dynamic_split=False):
    """
    Charge et filtre les données depuis un fichier CSV, adapté aux fichiers bien ou mal formatés.

    Args:
        filepath (str): Chemin du fichier CSV à charger.
        columns_to_keep (list, optional): Liste des colonnes à conserver. Si None, garde toutes les colonnes disponibles.
        dynamic_split (bool, optional): Indique si une séparation dynamique des colonnes doit être effectuée.

    Returns:
        pd.DataFrame: Les données filtrées et nettoyées.
    """
    print(f"Chargement des données depuis {filepath}...")

    try:
        # Charger les données avec ou sans séparation dynamique
        if dynamic_split:
            print("[INFO] Mode de séparation dynamique activé...")
            # Charger les données brutes comme une seule colonne
            data_raw = pd.read_csv(filepath, header=None)
            print("[DEBUG] Données brutes chargées avec succès. Tentative de séparation des colonnes...")

            # Séparer les colonnes si elles sont fusionnées
            data = data_raw[0].str.split(",", expand=True)

            # Définir un en-tête dynamique
            header = [
                "event-id", "visible", "timestamp", "location-long", "location-lat",
                "algorithm-marked-outlier", "argos:lat1", "argos:lat2", "argos:lc",
                "argos:location-algorithm", "argos:lon1", "argos:lon2", "comments",
                "modelled", "sensor-type", "individual-taxon-canonical-name",
                "tag-local-identifier", "individual-local-identifier", "study-name",
                "extra1", "extra2", "extra3"
            ]
            # Ajuster le nombre de colonnes
            header = header[:data.shape[1]]
            data.columns = header

        else:
            print("[INFO] Chargement direct avec en-tête détecté...")
            # Charger les données directement avec l'en-tête
            data = pd.read_csv(filepath, sep=",", header=0)

        print(f"[DEBUG] Nombre de colonnes détectées : {data.shape[1]}")
        print("[DEBUG] Colonnes détectées :")
        print(data.columns.tolist())

        # Nettoyer les données
        data = data.dropna(how="all")  # Supprimer les lignes entièrement vides
        if "event-id" in data.columns:
            data = data[
                ~data['event-id'].astype(str).str.contains("event-id", na=False)]  # Supprimer les lignes de doublons

        # Filtrer les colonnes si nécessaire
        if columns_to_keep:
            existing_columns = [col for col in columns_to_keep if col in data.columns]
            missing_columns = [col for col in columns_to_keep if col not in data.columns]

            if missing_columns:
                print(f"[WARNING] Colonnes manquantes : {missing_columns}")
            if existing_columns:
                data = data[existing_columns]
                print(f"[DEBUG] Colonnes conservées : {existing_columns}")

        print(f"[DEBUG] Données chargées : {len(data)} lignes.")
        print("Aperçu des premières lignes :")
        print(data.head())

        return data

    except Exception as e:
        print(f"[ERROR] Erreur lors du chargement des données : {e}")
        return pd.DataFrame()


def save_as_geojson(data, output_filepath):
    """
    Convertit un DataFrame en GeoJSON et le sauvegarde dans un fichier.

    Args:
        data (pd.DataFrame): Données à convertir.
        output_filepath (str): Chemin du fichier GeoJSON de sortie.
    """
    try:
        print("[INFO] Conversion des données en GeoJSON...")

        # Vérifier que les colonnes nécessaires sont présentes
        if 'location-lat' not in data.columns or 'location-long' not in data.columns:
            raise ValueError("Les colonnes 'location-lat' et 'location-long' sont requises pour le GeoJSON.")

        # Créer une colonne 'geometry' avec des objets Point
        geometry = [Point(xy) for xy in zip(data['location-long'], data['location-lat'])]
        geo_data = gpd.GeoDataFrame(data, geometry=geometry)

        # Définir le système de coordonnées (WGS84)
        geo_data.set_crs(epsg=4326, inplace=True)

        # Sauvegarder en GeoJSON
        geo_data.to_file(output_filepath, driver="GeoJSON")
        print(f"[INFO] Données GeoJSON sauvegardées dans : {output_filepath}")

    except Exception as e:
        print(f"[ERROR] Erreur lors de la conversion en GeoJSON : {e}")


if __name__ == "__main__":
    # Exemple d'utilisation
    filepath = "../../data/raw/White Stork Bulgaria.csv"
    corrected_filepath = "../../data/cleaned/corrected_data.csv"
    geojson_filepath = "../../data/cleaned/corrected_data.geojson"

    # Colonnes essentielles que l'on souhaite conserver
    columns_to_keep = ["timestamp", "location-long", "location-lat", "event-id"]

    # Charger et nettoyer les données
    is_storks_file = "Storks" in filepath
    data = load_data(filepath, columns_to_keep=columns_to_keep, dynamic_split=is_storks_file)

    # Sauvegarder les données nettoyées en CSV
    if not data.empty:
        data.to_csv(corrected_filepath, index=False)
        print(f"\n[INFO] Fichier corrigé sauvegardé dans : {corrected_filepath}")

        # Convertir en GeoJSON
        save_as_geojson(data, geojson_filepath)
    else:
        print("\n[INFO] Aucune donnée n'a été sauvegardée.")
