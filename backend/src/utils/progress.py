import json
from pathlib import Path

PROGRESS_FILE = Path("logs/ingest_progress.json")

def update_progress(phase: str, progress: int):
    data = {
        "phase": phase,
        "progress": progress
    }
    with open(PROGRESS_FILE, "w") as f:
        json.dump(data, f)

def reset_progress():
    update_progress("idle", 0)
