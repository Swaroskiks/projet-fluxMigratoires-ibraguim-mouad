"""Configuration File

- Server configuration (HOST, PORT, DEBUG)
- Data directory paths (DATA_RAW_DIR, DATA_CLEANED_DIR)
- Movebank API credentials (MOVEBANK_USERNAME, MOVEBANK_PASSWORD, MOVEBANK_BASE_URL)
"""

import os
from dotenv import load_dotenv
from pathlib import Path
from typing import Optional, Final

load_dotenv()

# ----------------------------
# Server Configuration
# ----------------------------
HOST: Final[str] = "127.0.0.1"
"""Server IP address (default: localhost)."""

PORT: Final[int] = 8050
"""Server listening port (default: 8050)."""

DEBUG: Final[bool] = False
"""Enable debug mode (True) or not (False)."""

# ----------------------------
# Data Directory Configuration
# ----------------------------
DATA_RAW_DIR: Final[Path] = Path("data", "raw")
DATA_RAW_DIR.mkdir(parents=True, exist_ok=True)
"""Directory for raw data."""

DATA_CLEANED_DIR: Final[Path] = Path("data", "cleaned")
DATA_CLEANED_DIR.mkdir(parents=True, exist_ok=True)
"""Directory for cleaned data."""

# ----------------------------
# Movebank API Access Configuration
# ----------------------------
MOVEBANK_USERNAME: Optional[str] = os.getenv("MOVEBANK_USERNAME")
"""Username for the Movebank API, loaded from .env."""

MOVEBANK_PASSWORD: Optional[str] = os.getenv("MOVEBANK_PASSWORD")
"""Password for the Movebank API, loaded from .env."""

MOVEBANK_BASE_URL: Final[str] = "https://www.movebank.org/movebank/service/direct-read"
"""Base URL for Movebank API requests."""
