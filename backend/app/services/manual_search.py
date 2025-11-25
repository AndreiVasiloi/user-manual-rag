import os
import requests

def get_serpapi_key():
    """Always fetch fresh key at call time."""
    return os.getenv("SERPAPI_KEY")

def search_manual_online(model: str) -> str | None:
    api_key = get_serpapi_key()

    if not api_key:
        print("ERROR: SerpAPI key is missing")
        return None

    params = {
        "engine": "google",
        "q": f"{model} site:manualsonline.com manual",
        "num": 5,
        "api_key": api_key
    }

    resp = requests.get("https://serpapi.com/search", params=params)

    if resp.status_code != 200:
        print("SerpAPI error:", resp.text)
        return None

    data = resp.json()

    for result in data.get("organic_results", []):
        link = result.get("link", "")
        if "manualsonline.com" in link:
            return link

    return None
