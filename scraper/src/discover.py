from bs4 import BeautifulSoup
from urllib.parse import urljoin
import requests
import os
import time

MAX_PAGES = 3
BASE_CATALOGUE_URL = "https://books.toscrape.com/catalogue/page-1.html"
HEADERS = {
    "User-Agent": "FlyRankInternshipA9/1.0 (+https://github.com/hussaingillani215-sketch/flyrank-week2-crud-api)"
}

def fetch_catalogue_page(page_num, url):
    cache_path = f"cache/catalogue-page-{page_num}.html"
    if os.path.exists(cache_path):
        with open(cache_path, "r", encoding="utf-8") as f:
            return f.read()

    response = requests.get(url, headers=HEADERS, timeout=5)
    if response.status_code != 200:
        raise Exception(f"Fetch failed: status {response.status_code}")

    time.sleep(0.5)
    with open(cache_path, "w", encoding="utf-8") as f:
        f.write(response.text)
    return response.text

def discover_all_book_urls():
    all_urls = []
    current_url = BASE_CATALOGUE_URL
    page_num = 1

    while current_url and page_num <= MAX_PAGES:
        html = fetch_catalogue_page(page_num, current_url)
        soup = BeautifulSoup(html, "html.parser")

        book_links = soup.select(".product_pod h3 a")
        for link in book_links:
            absolute_url = urljoin(current_url, link["href"])
            all_urls.append(absolute_url)

        next_link = soup.select_one("li.next a")
        if next_link and page_num < MAX_PAGES:
            current_url = urljoin(current_url, next_link["href"])
            page_num += 1
        else:
            current_url = None

    unique_urls = list(set(all_urls))
    print(f"catalogue_pages={page_num}, discovered={len(all_urls)}, unique_urls={len(unique_urls)}")
    return unique_urls

if __name__ == "__main__":
    discover_all_book_urls()
