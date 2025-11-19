from pathlib import Path
import json

from app.ingestion.pipeline.page_renderer import render_pdf_to_images
from app.ingestion.icon_processing.icon_detector import extract_icons_from_page
from app.ingestion.icon_processing.icon_deduplicator import deduplicate_icons

from app.ingestion.icon_processing.icon_classifier_batched import IconClassifierBatched

from app.core.config import GOOGLE_API_KEY, GEMINI_MODEL


def ingest_manual(pdf_path: str, out_dir: str):
    """
    Full ingestion pipeline:
    - Render PDF pages
    - Extract icon crops
    - Deduplicate icons
    - Classify icons with Gemini
    - Save metadata inside out_dir
    """
    out_dir = Path(out_dir)

    pages_dir = out_dir / "pages"
    icons_dir = out_dir / "icons"
    pages_dir.mkdir(parents=True, exist_ok=True)
    icons_dir.mkdir(parents=True, exist_ok=True)

    # Clean old icons before extraction
    for f in icons_dir.glob("*.png"):
        f.unlink()

    print("Rendering PDF pages to images...")
    render_pdf_to_images(pdf_path, pages_dir)

    print("Extracting icons from pages...")
    all_icons = []

    for page_img in pages_dir.glob("*.png"):
        icons = extract_icons_from_page(str(page_img), icons_dir)
        all_icons.extend(icons)

    print(f"✓ Extracted {len(all_icons)} raw icon crops.")

    # Save raw metadata
    with open(out_dir / "icons_raw_meta.json", "w", encoding="utf-8") as f:
        json.dump(all_icons, f, indent=2)

    print("De-duplicating icons...")
    clusters_path = out_dir / "icons_clusters.json"

    deduplicate_icons(
        icons_dir=str(icons_dir),
        output_json=str(clusters_path)
    )

    print("Deduplicating from:", icons_dir)
    print("Files in folder:", len(list(icons_dir.glob('*.png'))))

    # ------------------------------
    # STEP 3: Icon classification pipeline
    # ------------------------------

    print("Classifying icons with Gemini Vision (filtered + batched)...")

    classifier = IconClassifierBatched(
        api_key=GOOGLE_API_KEY,
        model_name=GEMINI_MODEL
    )

    classifier.classify_clusters(
        clusters_path=str(clusters_path),
        output_path=str(out_dir / "icons_classified.json"),
        batch_size=10
    )

    print("Ingest complete.")


# -----------------------------------------------------
# CLI usage (optional)
# Always uses the NEW folder structure under app/data
# -----------------------------------------------------
if __name__ == "__main__":
    BASE_DIR = Path(__file__).resolve().parents[3]  # backend/
    APP_DIR = BASE_DIR / "app"

    PDF_PATH = APP_DIR / "data" / "manuals" / "user_manual.pdf"
    OUT_DIR = APP_DIR / "data" / "processed" / "user_manual"

    ingest_manual(str(PDF_PATH), str(OUT_DIR))
