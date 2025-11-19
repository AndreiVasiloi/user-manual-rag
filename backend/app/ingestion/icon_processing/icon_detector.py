import cv2
import numpy as np
from pathlib import Path


def extract_icons_from_page(
    page_image_path: str,
    output_dir: str,
    min_area=600,           # minimum number of pixels in the contour
    max_area=30000,         # avoid capturing large diagram chunks
    min_solidity=0.5,       # solidity filter (exclude letters)
    max_aspect_ratio=2.0    # exclude long thin shapes (lines, borders)
):
    """
    Highly filtered icon extractor for manuals with vector-based icons.
    Removes letters, line fragments, and diagram parts.
    """

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    image = cv2.imread(page_image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Threshold to isolate shapes
    _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)

    # Morphological close to remove noise
    kernel = np.ones((4, 4), np.uint8)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    icons = []
    page_name = Path(page_image_path).stem
    page_h, page_w = gray.shape

    for idx, cnt in enumerate(contours):
        x, y, w, h = cv2.boundingRect(cnt)
        area = w * h

        # --- Filter 1: area filtering ---
        if area < min_area:
            continue
        if area > max_area:
            continue

        # --- Filter 2: aspect ratio ---
        aspect_ratio = max(w / h, h / w)
        if aspect_ratio > max_aspect_ratio:
            continue

        # --- Filter 3: solidity ---
        contour_area = cv2.contourArea(cnt)
        solidity = contour_area / float(area)
        if solidity < min_solidity:
            continue

        # --- Filter 4: remove shapes too close to page edges (layout artifacts) ---
        if x < 20 or y < 20 or (x + w) > (page_w - 20) or (y + h) > (page_h - 20):
            continue

        # --- Filter 5: pixel density (skip very empty shapes) ---
        crop = thresh[y:y+h, x:x+w]
        density = np.mean(crop / 255)
        if density < 0.15:  # extremely empty
            continue

        # Save icon
        crop_img = image[y:y+h, x:x+w]
        out_path = output_dir / f"{page_name}_icon_{idx:04}.png"
        cv2.imwrite(str(out_path), crop_img)

        icons.append({
            "file": str(out_path),
            "bbox": (x, y, w, h),
            "area": area,
            "solidity": solidity,
            "density": float(density)
        })

    return icons
