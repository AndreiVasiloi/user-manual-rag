from pathlib import Path
from PIL import Image
import imagehash
import json


def hash_icon(path: str) -> str:
    """Return a perceptual hash for the given icon image."""
    img = Image.open(path).convert("L")
    return str(imagehash.phash(img))


def deduplicate_icons(icons_dir: str, output_json: str, similarity_threshold: int = 5):
    """
    Detect duplicate icons using perceptual hashing.
    Icons with phash distance <= threshold are considered duplicates.
    Saves clusters to a JSON file.
    """

    icons_dir = Path(icons_dir)
    icons = list(icons_dir.glob("*.png"))

    icon_hashes = {}
    clusters = []

    for icon in icons:
        h = imagehash.phash(Image.open(icon).convert("L"))

        # Try to match to an existing cluster
        found_cluster = None
        for cluster in clusters:
            representative_hash = cluster["hash"]
            if h - representative_hash <= similarity_threshold:
                cluster["files"].append(str(icon))
                found_cluster = cluster
                break

        # If not matched, create new cluster
        if not found_cluster:
            clusters.append({
                "hash": h,
                "files": [str(icon)]
            })

    # Convert hashes to strings for JSON
    output = []
    for c in clusters:
        output.append({
            "hash": str(c["hash"]),
            "files": c["files"]
        })

    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    print(f"Found {len(clusters)} unique icon clusters (from {len(icons)} total).")

    return output
