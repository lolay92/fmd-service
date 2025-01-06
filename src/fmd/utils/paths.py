from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[3]
CONFIG_PATH = Path(BASE_DIR, "src/data_services/config")

# Output locations
OUT_DIR = Path(BASE_DIR, "out")
HIST_DATA_PATH = Path(OUT_DIR, "historical")
METADATA_PATH = Path(OUT_DIR, "metadata")
CRYPTO_PATH = Path(OUT_DIR, "crypto")

OUT_DIR.mkdir(parents=True, exist_ok=True)
METADATA_PATH.mkdir(parents=True, exist_ok=True)
