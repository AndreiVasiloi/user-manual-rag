import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import actual router modules
import app.api.routers.ask_router as ask_router
import app.api.routers.upload_router as upload_router
import app.api.routers.status_router as status_router

from app.rag.vector_store import LocalVectorStore


# -----------------------------------
# Environment variables (cache/temp)
# -----------------------------------
os.environ["TMPDIR"] = "D:/rag_temp"
os.environ["TEMP"] = "D:/rag_temp"
os.environ["TMP"] = "D:/rag_temp"

os.environ["HF_HOME"] = "D:/rag_temp/hf"
os.environ["SENTENCE_TRANSFORMERS_HOME"] = "D:/rag_temp/hf"


# -----------------------------------
# FastAPI initialization
# -----------------------------------
app = FastAPI()


# CORS for Angular
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global vector store (shared across routers)
vector_store = None


def startup_event():
    """
    Automatically load a default manual if it exists.
    Now uses the *new* folder structure:
    backend/app/data/processed/user_manual/...
    """
    BASE_DIR = Path(__file__).resolve().parents[1]  # backend/app
    DEFAULT_PROCESSED_DIR = BASE_DIR / "data" / "processed"

    default_rag_path = DEFAULT_PROCESSED_DIR / "user_manual" / "rag_chunks_with_embeddings.json"

    if default_rag_path.exists():
        global vector_store
        vector_store = LocalVectorStore(str(default_rag_path))

        # Share loaded vector store with ask_router
        ask_router.vector_store = vector_store

        print("✓ Loaded default manual automatically on startup.")


# Register the startup event
app.add_event_handler("startup", startup_event)


# -----------------------------------
# Register routers
# -----------------------------------
app.include_router(upload_router.router)
app.include_router(ask_router.router)
app.include_router(status_router.router)


@app.get("/")
def root():
    return {"message": "RAG backend (icon-aware) is running 🚀"}
