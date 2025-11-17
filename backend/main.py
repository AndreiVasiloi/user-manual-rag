import os

os.environ["TMPDIR"] = "D:/rag_temp"
os.environ["TEMP"] = "D:/rag_temp"
os.environ["TMP"] = "D:/rag_temp"

# HuggingFace / SentenceTransformers cache
os.environ["HF_HOME"] = "D:/rag_temp/hf"
os.environ["SENTENCE_TRANSFORMERS_HOME"] = "D:/rag_temp/hf"


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

from routers import ask_router, status_router, upload_router
from src.rag.vector_store import LocalVectorStore

app = FastAPI()

# CORS for Angular
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global vector store (None until a manual is uploaded)
vector_store = None

# Inject shared state into routers
ask_router.vector_store = None
upload_router.vector_store = None

def startup_event():
    """
    Optional: auto-load default manual at startup if present.
    If you prefer to load *only after upload*, comment this block out.
    """

    default_rag_path = Path("data_processed/user_manual/rag_chunks_with_embeddings.json")

    if default_rag_path.exists():
        global vector_store
        vector_store = LocalVectorStore(str(default_rag_path))

        # Share store with routers
        ask_router.vector_store = vector_store
        upload_router.vector_store = vector_store

        print("✓ Loaded default manual automatically on startup.")


# Register routers
app.include_router(upload_router.router)
app.include_router(ask_router.router)
app.include_router(status_router.router)

@app.get("/")
def root():
    return {"message": "RAG backend (icon-aware) is running 🚀"}
