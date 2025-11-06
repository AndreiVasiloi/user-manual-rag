from helpers.chunker import chunk_text
from routers import ask_router, upload_router
from src.loader import extract_text_from_pdf
from src.vector_store import create_vector_store
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# ✅ Allow requests from Angular frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Load manual once at startup
manual_path = Path("data/manuals/user_manual.pdf")
docs, index, vectors = [], None, None

if manual_path.exists():
    text = extract_text_from_pdf(manual_path)
    docs = chunk_text(text, chunk_size=1000, overlap=200)
    index, vectors = create_vector_store(docs)
    print(f"✅ Loaded default manual ({len(docs)} chunks)")

# ✅ Share state between routers
ask_router.docs = upload_router.docs = docs
ask_router.index = upload_router.index = index
ask_router.vectors = upload_router.vectors = vectors

# ✅ Register routers
app.include_router(upload_router.router)
app.include_router(ask_router.router)

@app.get("/")
def root():
    return {"message": "RAG backend is running 🚀"}
