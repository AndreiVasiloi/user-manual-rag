from fastapi import APIRouter, UploadFile, File
from pathlib import Path
import shutil

from src.ingest.full_ingest import run_full_ingestion
from src.rag.vector_store import LocalVectorStore
import routers.ask_router as ask_router

router = APIRouter(prefix="/upload", tags=["Upload"])

UPLOAD_DIR = Path("data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@router.post("/")
async def upload_manual(file: UploadFile = File(...)):
    """Upload a manual and run icon-aware ingestion."""
    # Save file
    file_path = UPLOAD_DIR / file.filename
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Prepare output folder
    output_dir = f"data_processed/{file.filename.replace('.pdf', '')}"

    # Run ingestion (now safe + silent)
    run_full_ingestion(str(file_path), output_dir)

    # Load vector store
    rag_file = Path(output_dir) / "rag_chunks_with_embeddings.json"
    vs = LocalVectorStore(str(rag_file))

    ask_router.vector_store = vs

    return {"message": "Manual uploaded and ingested successfully."}
