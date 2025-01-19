"""Movebank Data Retrieval Module.

This module handles downloading migration data from the Movebank API.
It provides functions to:
- Connect to the Movebank API
- Retrieve data by species
- Download data files
- Handle connection and download errors
"""

import os
from config import MOVEBANK_BASE_URL, MOVEBANK_USERNAME, MOVEBANK_PASSWORD, DATA_RAW_DIR
import requests
import hashlib
from src.utils.data_manager import load_species_metadata

def download_movebank_data(movebank_id: str, output_file: str) -> bool:
    """Downloads migration data for a given species from the Movebank API.

    Args:
        movebank_id (str): Movebank species identifier
        output_file (str): Path to the output file for downloaded data

    Returns:
        bool: True if the download was successful, False otherwise
    """
    session = requests.Session()
    
    params = {
        "entity_type": "event",
        "study_id": movebank_id,
        "attributes": "all"
    }

    auth = (str(MOVEBANK_USERNAME), str(MOVEBANK_PASSWORD)) if MOVEBANK_USERNAME and MOVEBANK_PASSWORD else None
    # First request to obtain license terms
    response = session.get(MOVEBANK_BASE_URL, params=params, auth=auth)
    
    if "License Terms:" in response.text:
        print("[INFO] Accepting license terms...")

        # Compute MD5 hash of the license content
        license_content = response.text.encode('utf-8')
        md5_hash = hashlib.md5(license_content).hexdigest()
        print(f"[DEBUG] Generated MD5 hash: {md5_hash}")

        # New request with MD5 hash
        params["license-md5"] = md5_hash
        response = session.get(MOVEBANK_BASE_URL, params=params, auth=auth)

    # Verification and saving the data
    if response.status_code == 200 and not response.text.startswith("<html>"):
        with open(output_file, "wb") as file:
            file.write(response.content)
        print(f"[INFO] Data downloaded to '{output_file}'")
        return True
    else:
        print(f"[ERROR] Download failed: {response.status_code}")
        print("[DEBUG] Response content:", response.text[:500])
        return False

def download_all_species_data() -> None:
    """Downloads migration data for all species.

    This function uses `download_movebank_data` to download data for each species.
    """
    species_metadata = load_species_metadata()
    success_count = 0
    total_count = len(species_metadata['datasets'])

    for dataset in species_metadata['datasets']:
        movebank_id = dataset['movebank_id']
        output_file = os.path.join(DATA_RAW_DIR, f"{dataset['id']}_raw.csv")
        
        print(f"\n[INFO] Downloading data for {dataset['name']} (ID: {movebank_id})")
        if download_movebank_data(movebank_id, output_file):
            success_count += 1

    print(f"\n[INFO] Download completed: {success_count}/{total_count} studies successfully downloaded")