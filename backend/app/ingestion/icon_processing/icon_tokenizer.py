import json
from pathlib import Path
import re


def normalize_label(label: str) -> str:
    """Convert Gemini's label into a safe token."""
    label = label.lower()
    label = re.sub(r"[^a-z0-9]+", "_", label)
    return label.strip("_")


def generate_icon_token_map(classified_path: str, output_path: str):
    """
    Create a mapping of cluster_id → semantic token → classification info.
    """

    classified = json.load(open(classified_path, "r", encoding="utf-8"))
    results = []

    for item in classified:
        label = item["classification"]["label"]
        normalized = normalize_label(label)
        token = f"<icon:{normalized}>"

        results.append({
            "cluster_id": item["cluster_id"],
            "token": token,
            "label": label,
            "meaning": item["classification"]["meaning"],
            "description": item["classification"]["description"],
            "representative": item["representative"]
        })

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"Saved icon token map to {output_path}")
