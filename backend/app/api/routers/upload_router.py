from fastapi import APIRouter, UploadFile, File
from pathlib import Path
import shutil

import app.api.routers.ask_router as ask_router
from app.ingestion.pipeline.full_ingest import run_full_ingestion
from app.rag.vector_store import LocalVectorStore

router = APIRouter(prefix="/upload", tags=["Upload"])

# ---------------------------------------------
# Base directories (always absolute & stable)
# backend/app/...
# ---------------------------------------------
from app.core.paths import UPLOAD_DIR, PROCESSED_DIR


UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/")
async def upload_manual(file: UploadFile = File(...)):
    """Upload a manual and run icon-aware ingestion."""

    # 1. Save uploaded file
    file_path = UPLOAD_DIR / file.filename
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 2. Prepare output folder inside app/data/processed
    manual_name = file.filename.replace(".pdf", "")
    output_dir = PROCESSED_DIR / manual_name
    output_dir.mkdir(parents=True, exist_ok=True)

    # 3. Run ingestion
    run_full_ingestion(str(file_path), str(output_dir))

    # 4. Load vector store
    rag_file = output_dir / "rag_chunks_with_embeddings.json"
    vs = LocalVectorStore(str(rag_file))

    ask_router.vector_store = vs

    return {"message": "Manual uploaded and ingested successfully."}
