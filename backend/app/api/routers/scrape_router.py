import os
import subprocess
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.ingestion.process_pdf import process_pdf
from app.rag.vector_store import LocalVectorStore
import app.api.routers.ask_router as ask_router  # set active vector store


router = APIRouter(prefix="/scrape", tags=["Scraping"])


class ScrapeRequest(BaseModel):
    # URL ales de user din /search/manual
    url: str


def find_scrapy_root() -> Path:
    """
    Găsește root-ul proiectului Scrapy:
      app/scrapers/manuals_scraper

    Înăuntru avem:
      manuals_scraper/     ← pachetul Scrapy (settings.py, spiders, pipelines)
      downloaded_pdfs/     ← FILES_STORE (folderul unde se salvează PDF-urile)
    """
    start = Path(__file__).resolve()
    for parent in start.parents:
        base = parent / "scrapers" / "manuals_scraper"
        if (base / "manuals_scraper" / "settings.py").exists():
            return base
    raise RuntimeError("Could not locate Scrapy project structure.")


def choose_spider_for_url(url: str) -> str:
    """Choose spider based on URL — only manualsonline.com allowed."""
    lower = url.lower()

    if "manualsonline.com" in lower:
        return "manualsonline"

    raise HTTPException(
        status_code=400,
        detail="Only manuals from manualsonline.com are currently supported.",
    )



@router.post("/manual")
async def scrape_manual(req: ScrapeRequest):
    """
    Scrape manual chosen by user:
    1. Receives a URL from manualsonline.com.
    2. Runs only the ManualOnline spider.
    3. Downloads PDF into downloaded_pdfs.
    4. Runs process_pdf (chunks + embeddings).
    5. Activates LocalVectorStore for /ask.
    """

    manual_url = req.url.strip()
    if not manual_url:
        raise HTTPException(status_code=400, detail="URL cannot be empty.")

    spider_name = choose_spider_for_url(manual_url)
    print(f"[SCRAPE] Using spider: {spider_name} for URL: {manual_url}")


    # 2) Find Scrapy project structure
    scrapy_project_root = find_scrapy_root()
    scrapy_cwd = scrapy_project_root / "manuals_scraper"   # aici e settings.py
    downloads_folder = scrapy_project_root / "downloaded_pdfs"

    downloads_folder.mkdir(parents=True, exist_ok=True)

    print(f"[SCRAPE] Scrapy root (cwd): {scrapy_cwd}")
    print(f"[SCRAPE] Downloads folder: {downloads_folder}")

    # 3) Clear old PDFs
    for f in downloads_folder.glob("*.pdf"):
        try:
            f.unlink()
        except Exception as e:
            print(f"[SCRAPE] Could not delete {f}: {e}")

    # 4) Run Scrapy spider cu start_url = manual_url
    result = subprocess.run(
        [
            "scrapy",
            "crawl",
            spider_name,
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


    # Validate it's actually a PDF
    if not latest_pdf.suffix.lower() == ".pdf":
        raise HTTPException(
            status_code=500,
            detail="Downloaded file is not a valid PDF. ManualsLib often blocks direct PDF access."
        )

    # 6) Ingest PDF → întoarce directorul cu datele RAG
    rag_dir = process_pdf(
        str(latest_pdf),
        metadata={"source_url": manual_url},
    )

    # 7) Initialize vector store and set as active pentru /ask
    from pathlib import Path

    rag_json_path = Path(rag_dir) / "rag_chunks_with_embeddings.json"

    if not rag_json_path.exists():
        raise HTTPException(
            status_code=500,
            detail=f"RAG JSON not found: {rag_json_path}"
        )

    vs = LocalVectorStore(str(rag_json_path))

    ask_router.vector_store = vs

    return {
        "message": "Manual scraped, downloaded, and processed successfully.",
        "scraped_url": manual_url,
        "pdf": latest_pdf.name,
        "rag_dir": rag_dir,
        "spider": spider_name,
    }
