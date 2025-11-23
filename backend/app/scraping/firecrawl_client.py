import requests
from typing import Any, Dict

from app.core.config import FIRECRAWL_API_KEY

FIRECRAWL_BASE_URL = "https://api.firecrawl.dev/v1"


class FirecrawlClient:
    """Thin wrapper around the Firecrawl HTTP API."""

    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key or FIRECRAWL_API_KEY
        if not self.api_key:
            raise ValueError("❌ FIRECRAWL_API_KEY is not set. Add it to your .env")

    @property
    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def scrape_url(self, url: str, formats: list[str] | None = None) -> Dict[str, Any]:
        """
        Scrape a single URL and return Firecrawl's response JSON.
        For ManualsLib we only need 'markdown'.
        """
        if formats is None:
            formats = ["markdown"]

        payload = {
            "url": url,
            "formats": formats,
        }

        resp = requests.post(
            f"{FIRECRAWL_BASE_URL}/scrape",
            headers=self._headers,
            json=payload,
            timeout=60,
        )
        resp.raise_for_status()
        data = resp.json()

        # Firecrawl usually returns: {"success": true, "data": {...}}
        if isinstance(data, dict) and "data" in data:
            return data["data"]
        return data
