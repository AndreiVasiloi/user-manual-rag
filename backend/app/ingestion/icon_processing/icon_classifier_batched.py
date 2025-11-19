import json
import time
from pathlib import Path
import cv2
import numpy as np

import google.generativeai as genai


# ============================================
# 1. Heuristic text/noise filter
# ============================================

def is_probably_text(img_path: str) -> bool:
    """
    Heuristic to remove text fragments before Gemini is called.
    """
    img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        return True

    h, w = img.shape

    # Very small images = likely text/noise
    if w < 25 or h < 20:
        return True

    # Text-like aspect ratios
    aspect = w / h
    if aspect > 5.0 or aspect < 0.2:
        return True

    # Black pixel ratio (text is thin)
    thresh = cv2.threshold(img, 200, 255, cv2.THRESH_BINARY_INV)[1]
    black_ratio = np.sum(thresh > 0) / (h * w)

    if black_ratio < 0.03:
        return True
    if black_ratio < 0.12:
        return True

    return False


# ============================================
# 2. Gemini prompts
# ============================================

ICON_DETECT_PROMPT = """
You must determine if the image is a REAL appliance icon
or just TEXT/NOISE.

Output ONLY one word:
ICON
TEXT
NOISE
"""

ICON_CLASSIFY_PROMPT = """
You are a domain expert for appliance manuals.
Classify ONLY REAL appliance icons.

Return STRICT JSON:
{
  "label": "...",
  "meaning": "...",
  "description": "...",
  "confidence": 0.0
}
"""


# ============================================
# 3. New Batch Classifier
# ============================================

class IconClassifierBatched:
    def __init__(self, api_key: str, model_name: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(
            model_name=model_name,
            generation_config={"temperature": 0}
        )

    def classify_clusters(self, clusters_path: str, output_path: str, batch_size=10):
        """
        clusters_path = json with:
        [
          {
            "hash": "...",
            "files": ["path1.png", "path2.png"]
          },
          ...
        ]
        """

        clusters = json.loads(Path(clusters_path).read_text())

        # We classify only the representative (first file)
        icon_paths = [c["files"][0] for c in clusters]

        final_results = []

        print(f"📦 Classifying {len(icon_paths)} icon clusters...")
        print(f"🔹 Using batch_size={batch_size} (Free Tier safe)")

        for start in range(0, len(icon_paths), batch_size):
            batch = icon_paths[start:start + batch_size]
            print(f"\n➡️ Batch {start // batch_size + 1} → {len(batch)} icons")

            # Process each icon in batch
            for img_path in batch:

                # 1) Heuristic first
                if is_probably_text(img_path):
                    continue

                img_bytes = Path(img_path).read_bytes()

                # 2) Check if real icon
                try:
                    detect_resp = self.model.generate_content(
                        [ICON_DETECT_PROMPT, img_bytes],
                        safety_settings={"HARASSMENT": "BLOCK_NONE"}
                    )
                    tag = detect_resp.text.strip().upper()
                except:
                    tag = "NOISE"

                if tag != "ICON":
                    continue

                # 3) Full classification
                try:
                    classify_resp = self.model.generate_content(
                        [ICON_CLASSIFY_PROMPT, img_bytes],
                        safety_settings={"HARASSMENT": "BLOCK_NONE"}
                    )
                    data = json.loads(classify_resp.text)
                except:
                    data = {
                        "label": "unknown",
                        "meaning": "unknown",
                        "description": "Failed to classify",
                        "confidence": 0.0
                    }

                final_results.append({
                    "path": img_path,
                    "label": data.get("label", "unknown"),
                    "meaning": data.get("meaning", "unknown"),
                    "description": data.get("description", ""),
                    "confidence": data.get("confidence", 0.0)
                })

            print("⏳ Cooldown 10 seconds to avoid rate limits...")
            time.sleep(10)

        # Save results
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(final_results, f, indent=2)

        print("✅ Icon classification completed successfully.")
        print(f"📁 Saved to: {output_path}")
