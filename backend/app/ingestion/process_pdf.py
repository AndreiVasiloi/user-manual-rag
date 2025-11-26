from pathlib import Path
from typing import Optional, Dict, Any

from app.core.logger import logger
from app.ingestion.pipeline.full_ingest import run_full_ingestion


def process_pdf(
    pdf_path: str,
    metadata: Optional[Dict[str, Any]] = None,
    output_root: str | None = None,
) -> str:
    """
    Universal ingestion entry point.
    - Used by BOTH upload and scraping.
    - Returns the FULL PATH to the final RAG JSON file (chunks + embeddings).

    metadata can include: model, brand, language, title, source_url...
    """

    pdf_path_p = Path(pdf_path)
    if not pdf_path_p.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path_p}")

    # Default output root: app/data/processed
    if output_root is None:
        output_root = Path(__file__).resolve().parents[1] / "data" / "processed"
    else:
        output_root = Path(output_root)

    output_root.mkdir(parents=True, exist_ok=True)

    # Decide folder name: prefer model, then title, then filename stem
    folder_name: Optional[str] = None
    if metadata:
        folder_name = metadata.get("model") or metadata.get("title")

    if not folder_name:
        folder_name = pdf_path_p.stem

    # Sanitize folder name
    folder_name = str(folder_name).replace("/", "_").replace("\\", "_").strip()

    output_dir = output_root / folder_name
    output_dir.mkdir(parents=True, exist_ok=True)

    logger.info(f"[process_pdf] Ingesting PDF: {pdf_path_p}")
    logger.info(f"[process_pdf] Output dir: {output_dir}")
    if metadata:
        logger.info(f"[process_pdf] Metadata: {metadata}")

    # Run your full ingestion pipeline
    run_full_ingestion(str(pdf_path_p), str(output_dir))

    # The ingestion pipeline always places RAG chunks here:
    rag_json = output_dir / "rag_chunks_with_embeddings.json"

    if not rag_json.exists():
        raise FileNotFoundError(
            f"RAG embedding file not found: {rag_json}. "
            f"run_full_ingestion() must generate rag_chunks_with_embeddings.json"
        )

    logger.info(f"[process_pdf] Returning output directory: {output_dir}")
    return str(output_dir)

