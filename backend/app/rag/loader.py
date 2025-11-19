# Extract text from a PDF file

import fitz  # PyMuPDF
fitz.TOOLS.mupdf_display_errors(False)
from pathlib import Path

def extract_text_from_pdf(pdf_path: str) -> str:
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text("text")
    return text
