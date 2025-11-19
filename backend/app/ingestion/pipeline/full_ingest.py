from pathlib import Path
from app.core.logger import logger
from app.rag.utils.progress import update_progress, reset_progress

from app.ingestion.ingest import ingest_manual
from app.ingestion.pipeline.build_knowledge import build_knowledge_base

def run_full_ingestion(pdf_path: str, output_dir: str):
    """
    Runs the entire ingestion pipeline with:
    - Progress tracking
    - Logging instead of printing
    - Safe execution for UI and VSCode
    """
    try:
        reset_progress()
        logger.info(f"Starting full ingestion for {pdf_path}")

        # 1. Icon extraction + classification
        update_progress("icons", 0)
        logger.info("Step 1/2: Extracting and classifying icons...")

        ingest_manual(pdf_path, output_dir)

        update_progress("icons", 100)
        logger.info("Icons extracted & classified.")

        # 2. Text + chunk + embedding
        update_progress("embedding", 0)
        logger.info("Step 2/2: Building text+embedding RAG dataset...")

        build_knowledge_base(
            pdf_path=pdf_path,
            classified_icons_path=f"{output_dir}/icons_classified.json",
            out_dir=output_dir,
        )

        update_progress("embedding", 100)
        logger.info("Ingestion complete.")

    except Exception as e:
        logger.error(f"Ingestion failed: {e}")
        update_progress("error", 0)
        raise
