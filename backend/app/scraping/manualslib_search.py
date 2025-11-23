import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
import re


def build_manualslib_search_url(query: str) -> str:
    """
    ManualsLib routes search queries based on the first letter
    of the first alphanumeric word in the query.
    Example:
        Saeco Poemia hd8325 -> /s/saeco+poemia+hd8325.html
        Bosch Climate 5000 -> /b/bosch+climate+5000.html
    """
    q = query.strip().lower()

    # Extract the first alphanumeric word
    first_word = re.sub(r"[^a-z0-9]+", "", q).strip()
    letter = first_word[0] if first_word else "s"

    encoded = quote_plus(q)  # produces saeco+poemia+hd8325
    return f"https://www.manualslib.com/{letter}/{encoded}.html"


def search_manualslib(query: str, limit: int = 5) -> list[dict]:
    """
    Search ManualsLib and return a list of manuals with title + url.
    Handles:
      - search results pages
      - product pages (auto-redirect)
    """
    url = build_manualslib_search_url(query)
    print("🔍 Generated URL:", url)

    headers = {
        # Prevent being treated like a bot
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }

    resp = requests.get(url, headers=headers, timeout=15)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    results = []

    # ==================================================
    # CASE 1 — SEARCH RESULTS PAGE
    # ==================================================
    # Newer ManualsLib layout
    for item in soup.select("div.searchitem a.manualitem_a"):
        href = item.get("href")
        title = item.get("title") or item.get_text(strip=True)
        if href:
            results.append({
                "title": title,
                "url": "https://www.manualslib.com" + href
            })
        if len(results) >= limit:
            return results

    # Older ManualsLib layout
    for item in soup.select("div.search-result-item a"):
        href = item.get("href")
        title = item.get("title") or item.get_text(strip=True)
        if href:
            results.append({
                "title": title,
                "url": "https://www.manualslib.com" + href
            })
        if len(results) >= limit:
            return results

    # ==================================================
    # CASE 2 — PRODUCT PAGE (your case!)
    # ==================================================
    # Example you uploaded contains .productlist entries
    for a in soup.select(".productlist a"):
        href = a.get("href")
        title = a.get("title") or a.get_text(strip=True)
        if href:
            results.append({
                "title": title,
                "url": "https://www.manualslib.com" + href
            })
        if len(results) >= limit:
            return results

    # ==================================================
    # CASE 3 — Fallback: any manual link in HTML
    # ==================================================
    for a in soup.select("a[href^='/manual/']"):
        href = a.get("href")
        title = a.get("title") or a.get_text(strip=True)
        results.append({
            "title": title,
            "url": "https://www.manualslib.com" + href
        })
        if len(results) >= limit:
            break

    return results
