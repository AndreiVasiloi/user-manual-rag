import os
import subprocess
from pathlib import Path

import requests
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.ingestion.process_pdf import process_pdf
from app.rag.vector_store import LocalVectorStore
import app.api.routers.ask_router as ask_router  # set active vector store


router = APIRouter(prefix="/scrape", tags=["Scraping"])


class ScrapeRequest(BaseModel):
    url: str  # URL returned from /search/manuals


# ---------------------------------------------------------
# Helper: Download PDF directly (Google-Fu mode)
# ---------------------------------------------------------
def download_pdf_direct(url: str, output_path: Path):
    print(f"[SCRAPE] Direct PDF detected → downloading: {url}")

    resp = requests.get(url, timeout=20)
    if resp.status_code != 200:
        raise HTTPException(500, f"PDF download failed ({resp.status_code})")

    output_path.write_bytes(resp.content)
    print(f"[SCRAPE] PDF saved to: {output_path}")

    return output_path


# ---------------------------------------------------------
# Helper: Locate Scrapy project
# ---------------------------------------------------------
def find_scrapy_root() -> Path:
    start = Path(__file__).resolve()
    for parent in start.parents:
        base = parent / "scrapers" / "manuals_scraper"
        if (base / "manuals_scraper" / "settings.py").exists():
            return base
    raise RuntimeError("Could not locate Scrapy project structure.")


# ---------------------------------------------------------
# Main endpoint
# ---------------------------------------------------------
@router.post("/manual")
async def scrape_manual(req: ScrapeRequest):
    """
    New Unified Scrape Logic:
    1) If URL ends with .pdf → download directly (Google-Fu mode)
    2) Else if URL from ManualOnline → use Scrapy spider
    3) Else → reject
    """

    manual_url = req.url.strip()
    if not manual_url:
        raise HTTPException(400, "URL cannot be empty.")

    url_lower = manual_url.lower()

    # -------------------------------------------------
    # CASE 1 — Direct PDF (Google-Fu)
    # -------------------------------------------------
    if url_lower.endswith(".pdf"):
        print("[SCRAPE] Mode: DIRECT PDF")

        # Create downloads folder
        scrapy_root = find_scrapy_root()
        downloads_folder = scrapy_root / "downloaded_pdfs"
        downloads_folder.mkdir(parents=True, exist_ok=True)

        # Clean old PDFs
        for f in downloads_folder.glob("*.pdf"):
            f.unlink()

        pdf_path = downloads_folder / "manual.pdf"
        download_pdf_direct(manual_url, pdf_path)

        # Process PDF with RAG pipeline
        rag_dir = process_pdf(
            str(pdf_path),
            metadata={"source_url": manual_url},
        )

        # Load vector store
        rag_json = Path(rag_dir) / "rag_chunks_with_embeddings.json"
        if not rag_json.exists():
            raise HTTPException(500, f"Missing RAG file: {rag_json}")

        ask_router.vector_store = LocalVectorStore(str(rag_json))

        return {
            "message": "PDF downloaded & processed successfully.",
            "scraped_url": manual_url,
            "pdf": pdf_path.name,
            "rag_dir": rag_dir,
            "mode": "direct_pdf",
        }

    # -------------------------------------------------
    # CASE 2 — ManualOnline (Scrapy mode)
    # -------------------------------------------------
    if "manualsonline.com" in url_lower:
        print("[SCRAPE] Mode: MANUALONLINE SCRAPING")

        spider_name = "manualsonline"

        scrapy_project_root = find_scrapy_root()
        scrapy_cwd = scrapy_project_root / "manuals_scraper"
        downloads_folder = scrapy_project_root / "downloaded_pdfs"

        downloads_folder.mkdir(parents=True, exist_ok=True)

        # Clear old PDFs
        for f in downloads_folder.glob("*.pdf"):
            f.unlink()

        # Run Scrapy
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

        if result.returncode != 0:
            print(result.stdout)
            print(result.stderr)
            raise HTTPException(500, "Scrapy failed. Check backend logs.")

        # Look for the PDF
        pdf_files = sorted(downloads_folder.glob("*.pdf"))
        if not pdf_files:
            raise HTTPException(404, "Scrapy finished but no PDF downloaded.")

        latest_pdf = pdf_files[-1]
        print(f"[SCRAPE] Using downloaded PDF: {latest_pdf}")

        # Process PDF with RAG pipeline
        rag_dir = process_pdf(
            str(latest_pdf),
            metadata={"source_url": manual_url},
        )

        # Load vector store
        rag_json = Path(rag_dir) / "rag_chunks_with_embeddings.json"
        if not rag_json.exists():
            raise HTTPException(500, f"Missing RAG file: {rag_json}")

        ask_router.vector_store = LocalVectorStore(str(rag_json))

        return {
            "message": "ManualOnline manual scraped & processed successfully.",
            "scraped_url": manual_url,
            "pdf": latest_pdf.name,
            "rag_dir": rag_dir,
            "mode": "scrapy_manualonline",
        }

    # -------------------------------------------------
    # CASE 3 — Unsupported Website
    # -------------------------------------------------
    raise HTTPException(
        400,
        "Unsupported URL. "
        "Use: direct PDF URLs or manuals from manualsonline.com.",
    )
