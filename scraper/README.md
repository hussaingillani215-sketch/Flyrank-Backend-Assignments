# Scraper — Books to Scrape

A polite scraping pipeline that collects 60 books from the first 3
catalogue pages of a public practice sandbox, turns raw HTML into
clean, schema-validated JSON, survives broken pages without crashing,
and reports what happened on every run.

## Target classification

- **Site:** books.toscrape.com
- **Why this site is appropriate:** The site's own homepage states it is a
  "demo website for web scraping purposes" and that prices/ratings are
  randomly assigned with no real meaning — it exists specifically for
  practicing scraping.
- **Scope:** the first 3 catalogue pages only (60 books total), no further.
- **Data collected:** title, product URL, price, availability, rating,
  description.
- **robots.txt result:** requested https://books.toscrape.com/robots.txt —
  returned 404 Not Found. No robots file exists on this site. A missing
  file is not permission on its own; the site's explicit "demo website for
  scraping" statement is what makes this target appropriate.

I will not reuse this code on another site without checking its rules and
terms first.

## Lane

Python 3, using requests, beautifulsoup4, and pydantic.

## How to run it

pip install -r requirements.txt
python src/normalize.py

This runs the full pipeline: discover the 3 catalogue pages, fetch and
extract all 60 book detail pages, normalize and validate every record,
and write the outputs below. First run takes ~30 seconds (politeness
delay between real requests); reruns are near-instant since pages are
cached.

## Output

- output/books.json — 60 validated book records
- output/errors.json — any records that failed schema validation
  (currently empty)
- output/run-report.json — summary of the last run

## Record schema

Each record in books.json has these fields:

- title (string) — Book title
- product_url (string) — Canonical identity, deduplicated on this
- price_text (string) — Raw price as shown on the page, e.g. £51.77
- price_gbp (number) — Parsed numeric price
- availability_text (string) — Raw stock text, e.g. "In stock (22 available)"
- rating_text (string or null) — Star rating word, e.g. "Three"
- description (string or null) — null if the book page had no description
- source_page (string) — Which catalogue page this book was found on
- fetched_at (string, ISO 8601) — UTC timestamp of when the page was fetched

## Politeness rules followed

- User-agent: every request identifies itself as FlyRankInternshipA9/1.0
  with a link back to this repo.
- Timeout: every request gives up after 5 seconds rather than hanging.
- Delay: at least 0.5 seconds between real requests to the site.
  Cached pages are read from disk and never re-hit the site.
- Status check: only a 200 response is treated as a real page.
  404 and 403 responses are never retried (the page does not exist, or
  the site said no). Timeouts and 5xx server errors get one retry.
- Caching: every fetched page is saved to cache/ so re-running the
  scraper during development never re-hits the live site.

## Why this needed no browser

The book data (title, price, availability, rating, description) is
already present in the raw HTML the server sends back - there is no
JavaScript rendering the content after the page loads. A browser would
only add cost (memory, launch time) here, not capability.

## Latest run report

run_started: 2026-08-30T20:31:53.976815+00:00
duration_seconds: 0.87
pages_fetched: 60
valid_records: 60
invalid_records: 0
failed_pages: 0
failed_page_details: []

Failure survival was tested by deliberately adding one fake book URL to
the discovered list: the run still finished, books.json still held
the 60 real records, and run-report.json correctly showed
failed_pages: 1 with a clear 404 reason.

## Ethics note

This scraper only targets a site that explicitly exists for scraping
practice. In general: use an official API when one exists, never bypass
logins, paywalls, or explicit blocks, and collect only the data actually
needed for the task.

## Known limitation

A small number of book descriptions on this site contain the same
opening text twice in the raw HTML (a source-data quirk, not a bug in
our extraction). Description deduplication detects this using a
15-character anchor match against the rest of the text - verified
against all 60 books in this run with no false positives, but a
description that naturally repeats its own opening phrase (e.g. certain
poetry) could theoretically be mis-trimmed by this approach.
