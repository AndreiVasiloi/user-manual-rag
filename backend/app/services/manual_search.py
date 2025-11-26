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

    queries = [
        f"{model} filetype:pdf manual",
        f"{model} pdf user manual",
        f"{model} download manual pdf",
        f"{model} instruction manual pdf",
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
            link = result.get("link", "").lower()

            if link.endswith(".pdf"):
                title = result.get("title", "PDF manual")
                results.append({
                    "title": title,
                    "url": link,
                    "source": "pdf"
                })

        if results:
            break

    return results


