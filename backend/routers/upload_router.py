from helpers.chunker import chunk_text
from src.loader import extract_text_from_pdf
from src.vector_store import create_vector_store
from fastapi import APIRouter, UploadFile, File
from pathlib import Path
import shutil

router = APIRouter(prefix="/upload", tags=["Upload"])

docs = []
index = None
vectors = None
UPLOAD_DIR = Path("data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@router.post("/")
async def upload_manual(file: UploadFile = File(...)):
    """Upload a new user manual (PDF)."""
    global docs, index, vectors

    # Save uploaded PDF to disk
    file_path = UPLOAD_DIR / file.filename
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Extract text and rebuild vector store
    text = extract_text_from_pdf(file_path)
    chunks = chunk_text(text, chunk_size=1000, overlap=200)
    index, vectors = create_vector_store(chunks)
    docs = chunks

    print(f"✅ Uploaded and indexed: {file.filename} ({len(chunks)} chunks)")
    return {"message": f"File '{file.filename}' uploaded and processed successfully."}
