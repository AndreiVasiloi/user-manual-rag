from pathlib import Path
import json

from src.ingest.page_renderer import render_pdf_to_images
from src.ingest.icon_detector import extract_icons_from_page
from src.ingest.icon_deduplicator import deduplicate_icons

# NEW: import the updated batched classifier
from src.ingest.icon_classifier_batched import IconClassifierBatched

from src.config import GOOGLE_API_KEY, GEMINI_MODEL


def ingest_manual(pdf_path: str, out_dir: str):
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
    # STEP 3: NEW CLEAN CLASSIFICATION PIPELINE
    # ------------------------------

    print("Classifying icons with Gemini Vision (filtered + batched)...")

    # Create Gemini classifier
    classifier = IconClassifierBatched(
        api_key=GOOGLE_API_KEY,
        model_name=GEMINI_MODEL
    )

    # Classify deduplicated clusters
    classifier.classify_clusters(
        clusters_path=str(clusters_path),
        output_path=str(out_dir / "icons_classified.json"),
        batch_size=10   # safe for Gemini free tier
    )

    print("Ingest complete.")


if __name__ == "__main__":
    ingest_manual(
        pdf_path="data/manuals/user_manual.pdf",
        out_dir="data_processed/user_manual"
    )
