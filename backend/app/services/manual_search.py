import requests
import os

SERP_API_KEY = os.getenv("SERPAPI_KEY")

def detect_source(url: str) -> str:
    url = url.lower()
    if "manualsonline.com" in url:
        return "manualsonline"
    if "manualslib.com" in url:
        return "manualslib"
    return "other"

def search_manual_online(model: str):
    if not SERP_API_KEY:
        print("SerpAPI KEY MISSING")
        return []

    # Clean model name (optional)
    model_clean = model.strip()

    # Queries focused ONLY on manualsOnLine
    queries = [
        f"{model_clean} site:manualsonline.com manual",
        f"{model_clean} ManualOnline manual",
        f"{model_clean} user manual manualsonline",
    ]

    results = []

    for q in queries:
        params = {
            "engine": "google",
            "q": q,
            "api_key": SERP_API_KEY,
            "num": 10,
        }

        resp = requests.get("https://serpapi.com/search", params=params)

        if resp.status_code != 200:
            continue

        data = resp.json()

        for result in data.get("organic_results", []):
            link = result.get("link", "")

            # ONLY accept manualsonline.com
            if "manualsonline.com" in link.lower():
                title = result.get("title", "Unknown")
                results.append({
                    "title": title,
                    "url": link,
                    "source": "manualsonline"
                })

        if results:
            break  # stop after first successful query

    return results

