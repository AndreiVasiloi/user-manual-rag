import requests

url = "https://www.manualslib.com/s/saeco+poemia+hd8325.html"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36"
}

resp = requests.get(url, headers=headers)
print(resp.text)
