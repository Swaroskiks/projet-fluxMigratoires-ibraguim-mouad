import pandas as pd


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


if __name__ == "__main__":
    # Exemple d'utilisation
    # Changez ce chemin pour tester avec différents fichiers
    filepath = "../../data/raw/White Stork Bulgaria.csv"
    output_filepath = "../../data/cleaned/corrected_data.csv"

    # Colonnes essentielles que l'on souhaite conserver
    columns_to_keep = ["timestamp", "location-long", "location-lat", "event-id"]

    # Dynamique pour détecter si les données sont mal formatées
    is_storks_file = "Storks" in filepath  # Déterminez dynamiquement si le fichier est mal formaté
    data = load_data(filepath, columns_to_keep=columns_to_keep, dynamic_split=is_storks_file)

    # Sauvegarder les données corrigées dans un nouveau fichier
    if not data.empty:
        data.to_csv(output_filepath, index=False)
        print(f"\n[INFO] Fichier corrigé sauvegardé dans : {output_filepath}")
    else:
        print("\n[INFO] Aucune donnée n'a été sauvegardée.")
