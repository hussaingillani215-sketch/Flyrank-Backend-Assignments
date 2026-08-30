from bs4 import BeautifulSoup
from datetime import datetime, timezone
from discover import discover_all_book_urls, fetch_catalogue_page
import requests
import os
import time
import json

HEADERS = {
    "User-Agent": "FlyRankInternshipA9/1.0 (+https://github.com/hussaingillani215-sketch/flyrank-week2-crud-api)"
}

def fetch_book_page(book_url, index):
    cache_path = f"cache/book-{index}.html"
    if os.path.exists(cache_path):
        with open(cache_path, "r", encoding="utf-8") as f:
            return f.read()

    response = requests.get(book_url, headers=HEADERS, timeout=5)
    if response.status_code != 200:
        raise Exception(f"Fetch failed: status {response.status_code} for {book_url}")
    response.encoding = "utf-8"

    time.sleep(0.5)
    with open(cache_path, "w", encoding="utf-8") as f:
        f.write(response.text)
    return response.text

def extract_record(book_url, source_page, html):
    soup = BeautifulSoup(html, "html.parser")

    title = soup.select_one("h1").get_text(strip=True)
    price_text = soup.select_one(".price_color").get_text(strip=True)
    availability_text = soup.select_one(".instock.availability").get_text(strip=True)

    rating_tag = soup.select_one(".star-rating")
    rating_text = rating_tag["class"][1] if rating_tag else None

    desc_tag = soup.select_one("#product_description ~ p")
    description = desc_tag.get_text(strip=True) if desc_tag else None

    return {
        "title": title,
        "product_url": book_url,
        "price_text": price_text,
        "availability_text": availability_text,
        "rating_text": rating_text,
        "description": description,
        "source_page": source_page,
        "fetched_at": datetime.now(timezone.utc).isoformat()
    }

def extract_all_records():
    book_urls = discover_all_book_urls()
    records = []

    for index, (book_url, source_page) in enumerate(book_urls.items(), start=1):
        html = fetch_book_page(book_url, index)
        record = extract_record(book_url, source_page, html)
        records.append(record)

    print(f"detail_pages={len(records)}")
    print(json.dumps(records[0], indent=2))
    return records

if __name__ == "__main__":
    extract_all_records()
