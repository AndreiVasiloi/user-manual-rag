from pathlib import Path

# backend/app
APP_DIR = Path(__file__).resolve().parents[1]

# backend/app/data
DATA_DIR = APP_DIR / "data"
UPLOAD_DIR = DATA_DIR / "uploads"
MANUALS_DIR = DATA_DIR / "manuals"
PROCESSED_DIR = DATA_DIR / "processed"

# Make sure folders exist
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
MANUALS_DIR.mkdir(parents=True, exist_ok=True)
