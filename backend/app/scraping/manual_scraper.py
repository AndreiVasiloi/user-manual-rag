from pathlib import Path
from urllib.parse import urlparse

from app.scraping.firecrawl_client import FirecrawlClient


def build_manual_folder_name(url: str) -> str:
    """
    For ManualsLib URLs like:
      https://www.manualslib.com/manual/12345/Product-Name.html
    We create folder: product-name-12345
    """
    parsed = urlparse(url)
    parts = [p for p in parsed.path.split("/") if p]

    # Defensive: expect ".../manual/<id>/<slug>.html"
    manual_id = "unknown"
    slug = "manual"

    if len(parts) >= 3 and parts[-3] == "manual":
        manual_id = parts[-2]
        slug_with_ext = parts[-1]  # Product-Name.html
        slug = slug_with_ext.rsplit(".", 1)[0]
    else:
        # fallback: last part as slug
        slug = parts[-1].rsplit(".", 1)[0]

    folder = f"{slug.lower()}-{manual_id}"
    folder = folder.replace(" ", "-")
    return folder


def scrape_manual_to_disk(url: str, processed_base_dir: Path) -> Path:
    """
    Scrape a ManualsLib URL with Firecrawl and save markdown to:
      processed_base_dir / <slug-id> / scraped.md
    Returns the manual directory path.
    """
    client = FirecrawlClient()
    result = client.scrape_url(url, formats=["markdown"])

    # Firecrawl returns markdown either directly or nested
    markdown = (
        result.get("markdown")
        if isinstance(result, dict)
        else None
    )
    if not markdown:
        raise ValueError(f"❌ Firecrawl did not return markdown for URL: {url}")

    manual_folder_name = build_manual_folder_name(url)
    manual_dir = processed_base_dir / manual_folder_name
    manual_dir.mkdir(parents=True, exist_ok=True)

    out_file = manual_dir / "scraped.md"
    out_file.write_text(markdown, encoding="utf-8")

    print(f"📄 Saved scraped markdown to: {out_file}")
    return manual_dir
