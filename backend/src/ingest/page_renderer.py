import fitz  # PyMuPDF
from pathlib import Path
fitz.TOOLS.mupdf_display_errors(False)

def render_pdf_to_images(pdf_path: str, output_dir: str, dpi: int = 200):
    """
    Render each page of the PDF into a high-resolution PNG image.
    This is required for extracting vector-based icons that do not exist as bitmap objects.
    """
    pdf_path = Path(pdf_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    doc = fitz.open(pdf_path)

    try:
        for page_index in range(len(doc)):
            page = doc[page_index]
            pix = page.get_pixmap(dpi=dpi)

            img_path = output_dir / f"page_{page_index+1:03}.png"
            pix.save(img_path)

        print(f"Rendered {len(doc)} pages to PNG.")
    finally:
        doc.close()


if __name__ == "__main__":
    render_pdf_to_images(
        pdf_path="data/manuals/user_manual.pdf",
        output_dir="data_processed/pages"
    )
