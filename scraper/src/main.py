import requests
import os

CACHE_PATH = "cache/catalogue-page-1.html"
URL = "https://books.toscrape.com/catalogue/page-1.html"
HEADERS = {
    "User-Agent": "FlyRankInternshipA9/1.0 (+https://github.com/hussaingillani215-sketch/flyrank-week2-crud-api)"
}

def fetch_page():
    if os.path.exists(CACHE_PATH):
        with open(CACHE_PATH, "r", encoding="utf-8") as f:
            html = f.read()
        print(f"CACHE HIT - {len(html)} bytes")
        return html

    response = requests.get(URL, headers=HEADERS, timeout=5)
    if response.status_code != 200:
        raise Exception(f"Fetch failed: status {response.status_code}")

    html = response.text
    with open(CACHE_PATH, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"FETCH - {len(html)} bytes")
    return html

if __name__ == "__main__":
    fetch_page()
