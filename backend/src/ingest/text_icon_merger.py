import fitz
import json
from pathlib import Path
fitz.TOOLS.mupdf_display_errors(False)

def merge_icons_into_text(pdf_path: str, tokens_path: str, output_path: str):
    """
    Very simple version:
    - Reads the PDF page by page
    - For each page, if it has icons, we prepend their tokens to the page text.
      (Good enough to make icons searchable and tied to the right context.)
    """

    tokens = json.load(open(tokens_path, "r", encoding="utf-8"))

    # Group tokens by page number using representative file name: page_003_icon_...
    tokens_by_page = {}
    for t in tokens:
        rep = Path(t["representative"]).stem  # e.g., page_003_icon_0004
        page_prefix = rep.split("_icon_")[0]  # "page_003"
        tokens_by_page.setdefault(page_prefix, []).append(t)

    doc = fitz.open(pdf_path)
    pages_text = []

    for page_index in range(len(doc)):
        page = doc[page_index]
        page_id = f"page_{page_index+1:03}"

        # Extract page text
        text = page.get_text("text")

        # If this page has icons, prepend their tokens
        page_tokens = tokens_by_page.get(page_id, [])
        if page_tokens:
            token_line = " ".join(t["token"] for t in page_tokens)
            enriched = token_line + "\n" + text
        else:
            enriched = text

        pages_text.append(enriched)

    doc.close()

    full_text = "\n\n".join(pages_text)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(full_text)

    print(f"Saved icon-enriched text to {output_path}")
