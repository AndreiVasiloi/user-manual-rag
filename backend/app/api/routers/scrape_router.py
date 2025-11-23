from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl

import app.api.routers.ask_router as ask_router
from app.scraping.manual_scraper import scrape_manual_to_disk
from app.rag.vector_store import LocalVectorStore
from app.core.config import CHUNK_SIZE, CHUNK_OVERLAP
# If you already have a text->rag builder, import it here instead of the stub
# from app.rag.text_ingest import build_rag_from_markdown

router = APIRouter(prefix="/scrape", tags=["Scrape"])


class ManualScrapeRequest(BaseModel):
    url: HttpUrl


# Base directory for processed data: backend/app/data/processed
BASE_DIR = Path(__file__).resolve().parents[2]  # backend/app
DATA_DIR = BASE_DIR / "data"
PROCESSED_DIR = DATA_DIR / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def build_rag_from_markdown_stub(markdown_path: Path) -> Path:
    """
    Stub that you can replace with your real pipeline.
    Expected to create rag_chunks_with_embeddings.json in the same folder.
    """
    # TODO: integrate with your existing RAG pipeline.
    # For now, just raise to remind you to implement:
    raise NotImplementedError(
        f"build_rag_from_markdown_stub not implemented. Got: {markdown_path}"
    )


@router.post("/manual")
async def scrape_manual(request: ManualScrapeRequest):
    """
    Scrape a ManualsLib URL using Firecrawl.
    """
    url = str(request.url)   # ✔ convert HttpUrl → str

    try:
        manual_dir = scrape_manual_to_disk(url, PROCESSED_DIR)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    markdown_path = manual_dir / "scraped.md"
    rag_file = manual_dir / "rag_chunks_with_embeddings.json"

    return {
        "message": "Manual scraped successfully.",
        "manual_folder": manual_dir.name,
        "scraped_markdown": str(markdown_path),
        "rag_ready": rag_file.exists(),
        "url": url  # ✔ always send string back
    }

