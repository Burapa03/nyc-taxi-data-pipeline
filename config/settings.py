
from pathlib import Path

# ==========================================
# PROJECT DIRECTORIES
# ==========================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
CURATED_DIR = DATA_DIR / "curated"

REPORT_DIR = PROJECT_ROOT / "reports"
DOCS_DIR = PROJECT_ROOT / "docs"


# ==========================================
# DATA CONFIGURATION
# ==========================================

YEAR = 2024
MONTHS = range(1, 7)

START_DATE = f"{YEAR}-01-01"
END_DATE = f"{YEAR}-07-01"


# ==========================================
# NYC TLC TAXI CONFIGURATION
# ==========================================

TAXI_CONFIG = {
    "Yellow Taxi": {
        "file_prefix": "yellow_tripdata",
        "pickup_column": "tpep_pickup_datetime"
    },

    "Green Taxi": {
        "file_prefix": "green_tripdata",
        "pickup_column": "lpep_pickup_datetime"
    },

    "FHV": {
        "file_prefix": "fhv_tripdata",
        "pickup_column": "pickup_datetime"
    },

    "HVFHV": {
        "file_prefix": "fhvhv_tripdata",
        "pickup_column": "pickup_datetime"
    }
}


# ==========================================
# DATA SOURCE
# ==========================================

BASE_URL = (
    "https://d37ci6vzurychx.cloudfront.net/"
    "trip-data"
)
