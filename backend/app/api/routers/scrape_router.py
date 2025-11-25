import os
import subprocess
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.manual_search import search_manual_online
from app.ingestion.process_pdf import process_pdf
from app.rag.vector_store import LocalVectorStore
import app.api.routers.ask_router as ask_router  # to set global vector_store


router = APIRouter(prefix="/scrape", tags=["Scraping"])


class ScrapeRequest(BaseModel):
    model: str


def find_scrapy_project_root() -> Path:
    """
    Find the Scrapy project root:
      app/scrapers/manuals_scraper

    Inside it we have:
      manuals_scraper/     ← Scrapy package (settings.py, spiders, pipelines)
      downloaded_pdfs/     ← Our FILES_STORE target
    """
    start = Path(__file__).resolve()
    for parent in start.parents:
        project_root = parent / "scrapers" / "manuals_scraper"
        settings_file = project_root / "manuals_scraper" / "settings.py"
        if settings_file.exists():
            return project_root

    raise RuntimeError("Could not locate Scrapy project root.")


@router.post("/manual")
async def scrape_manual(req: ScrapeRequest):
    """
    Scrape a manual by model name:
      1. Use SerpAPI to find a Manualsonline URL.
      2. Run Scrapy spider (manualsonline) on that URL.
      3. Locate downloaded PDF.
      4. Ingest PDF via process_pdf.
      5. Initialize vector store → becomes active manual for /ask.
    """
    model = req.model.strip()
    if not model:
        raise HTTPException(status_code=400, detail="Model cannot be empty.")

    # 1) Search for the manual online
    manual_url = search_manual_online(model)
    if not manual_url:
        raise HTTPException(
            status_code=404,
            detail="Could not find any manual online."
        )

    print(f"[SCRAPE] Found manual URL: {manual_url}")

    # 2) Locate Scrapy project structure
    scrapy_project_root = find_scrapy_project_root()
    scrapy_cwd = scrapy_project_root / "manuals_scraper"   # where settings.py is
    downloads_folder = scrapy_project_root / "downloaded_pdfs"

    downloads_folder.mkdir(parents=True, exist_ok=True)

    print(f"[SCRAPE] Scrapy root: {scrapy_cwd}")
    print(f"[SCRAPE] Downloads folder: {downloads_folder}")

    # 3) Clear old PDFs
    for f in downloads_folder.glob("*.pdf"):
        f.unlink()

    # 4) Run Scrapy spider
    result = subprocess.run(
        [
            "scrapy",
            "crawl",
            "manualsonline",
            "-a",
            f"start_url={manual_url}",
        ],
        cwd=scrapy_cwd,
        capture_output=True,
        text=True,
    )

    print("\n[SCRAPE] SCRAPY STDOUT:\n", result.stdout)
    print("\n[SCRAPE] SCRAPY STDERR:\n", result.stderr)

    if result.returncode != 0:
        raise HTTPException(
            status_code=500,
            detail="Scrapy failed. Check backend logs for details.",
        )

    # 5) Find downloaded PDF
    pdf_files = sorted(downloads_folder.glob("*.pdf"))
    if not pdf_files:
        raise HTTPException(
            status_code=404,
            detail="Scrapy finished, but no PDF was downloaded.",
        )

    latest_pdf = pdf_files[-1]
    print(f"[SCRAPE] Using downloaded PDF: {latest_pdf}")

    # 6) Ingest PDF → get RAG JSON path
    rag_json_path = process_pdf(
        str(latest_pdf),
        metadata={"model": model, "source_url": manual_url},
    )

    # 7) Initialize vector store and set as active
    vs = LocalVectorStore(rag_json_path)
    ask_router.vector_store = vs

    return {
        "message": "Manual scraped, downloaded, and processed successfully.",
        "scraped_url": manual_url,
        "pdf": latest_pdf.name,
        "rag_json": rag_json_path,
    }
