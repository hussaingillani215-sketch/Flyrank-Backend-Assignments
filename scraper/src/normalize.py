from pydantic import BaseModel, ValidationError
from typing import Optional
from urllib.parse import urlparse
import json
import sys
sys.path.insert(0, "src")
from extract import extract_all_records

def dedupe_text(text):
    if not text:
        return text
    length = len(text)
    if length % 2 == 0:
        half = length // 2
        first_half, second_half = text[:half], text[half:]
        if first_half == second_half:
            return first_half
    return text

def parse_price(price_text):
    cleaned = price_text.replace("£", "").strip()
    return float(cleaned)

class BookRecord(BaseModel):
    title: str
    product_url: str
    price_text: str
    price_gbp: float
    availability_text: str
    rating_text: Optional[str]
    description: Optional[str]
    source_page: str
    fetched_at: str

def normalize_and_validate():
    raw_records = extract_all_records()

    valid_records = []
    invalid_records = []
    seen_urls = set()

    for raw in raw_records:
        try:
            price_gbp = parse_price(raw["price_text"])
            description = dedupe_text(raw["description"])
            canonical_url = raw["product_url"]

            if canonical_url in seen_urls:
                continue  # duplicate by canonical URL - skip, don't store twice
            seen_urls.add(canonical_url)

            record = BookRecord(
                title=raw["title"],
                product_url=canonical_url,
                price_text=raw["price_text"],
                price_gbp=price_gbp,
                availability_text=raw["availability_text"],
                rating_text=raw["rating_text"],
                description=description,
                source_page=raw["source_page"],
                fetched_at=raw["fetched_at"]
            )
            valid_records.append(record.model_dump())

        except (ValidationError, ValueError) as e:
            invalid_records.append({"record": raw, "reason": str(e)})

    with open("output/books.json", "w", encoding="utf-8") as f:
        json.dump(valid_records, f, indent=2, ensure_ascii=False)

    with open("output/errors.json", "w", encoding="utf-8") as f:
        json.dump(invalid_records, f, indent=2, ensure_ascii=False)

    print(f"valid_records={len(valid_records)}, invalid_records={len(invalid_records)}")

if __name__ == "__main__":
    normalize_and_validate()
