from pydantic import BaseModel, ValidationError
from typing import Optional
import json
import sys
import time
from datetime import datetime, timezone
sys.path.insert(0, "src")
from extract import extract_all_records

def dedupe_text(text):
    if not text or len(text) < 80:
        return text
    anchor = text[:40]
    second_pos = text.find(anchor, 1)
    if second_pos != -1:
        return text[second_pos:]
    return text

def parse_price(price_text):
    return float(price_text.replace("£", "").strip())

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
    start_time = time.time()
    run_started = datetime.now(timezone.utc).isoformat()

    raw_records, failed_pages = extract_all_records()

    valid_records = []
    invalid_records = []
    seen_urls = set()

    for raw in raw_records:
        try:
            price_gbp = parse_price(raw["price_text"])
            description = dedupe_text(raw["description"])
            canonical_url = raw["product_url"]
            if canonical_url in seen_urls:
                continue
            seen_urls.add(canonical_url)
            record = BookRecord(
                title=raw["title"], product_url=canonical_url,
                price_text=raw["price_text"], price_gbp=price_gbp,
                availability_text=raw["availability_text"], rating_text=raw["rating_text"],
                description=description, source_page=raw["source_page"], fetched_at=raw["fetched_at"]
            )
            valid_records.append(record.model_dump())
        except (ValidationError, ValueError) as e:
            invalid_records.append({"record": raw, "reason": str(e)})

    with open("output/books.json", "w", encoding="utf-8") as f:
        json.dump(valid_records, f, indent=2, ensure_ascii=False)
    with open("output/errors.json", "w", encoding="utf-8") as f:
        json.dump(invalid_records, f, indent=2, ensure_ascii=False)

    duration = round(time.time() - start_time, 2)
    report = {
        "run_started": run_started,
        "duration_seconds": duration,
        "pages_fetched": len(raw_records) + len(failed_pages),
        "valid_records": len(valid_records),
        "invalid_records": len(invalid_records),
        "failed_pages": len(failed_pages),
        "failed_page_details": failed_pages
    }
    with open("output/run-report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"valid_records={len(valid_records)}, invalid_records={len(invalid_records)}, failed_pages={len(failed_pages)}")

if __name__ == "__main__":
    normalize_and_validate()
