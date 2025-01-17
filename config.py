import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

HOST = "127.0.0.1"
PORT = 8020
DEBUG = True

DATA_RAW_DIR = Path("data", "raw")
DATA_CLEANED_DIR = Path("data", "cleaned")

MOVEBANK_USERNAME = os.getenv("MOVEBANK_USERNAME")
MOVEBANK_PASSWORD = os.getenv("MOVEBANK_PASSWORD")
MOVEBANK_BASE_URL = f"https://www.movebank.org/movebank/service/direct-read"