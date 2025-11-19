from fastapi import APIRouter
from app.rag.utils.progress import PROGRESS_FILE
import json

router = APIRouter(prefix="/ingest", tags=["Ingest Status"])

@router.get("/status")
def get_ingest_status():
    if PROGRESS_FILE.exists():
        return json.loads(PROGRESS_FILE.read_text())
    return {"phase": "idle", "progress": 0}
