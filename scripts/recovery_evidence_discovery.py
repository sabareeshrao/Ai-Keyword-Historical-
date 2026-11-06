#!/usr/bin/env python3
"""Collect source-backed historical DATE CANDIDATES for undated recovery records.

This script deliberately does NOT modify KEYWORD_INVENTORY.csv or claim first-ever
use. Exact-phrase matches in dated titles or abstracts become proposals for
historical review, not automatic facts. Requires Python 3.10+, standard library.

Example:
    python scripts/recovery_evidence_discovery.py --limit 100
"""
import argparse
import csv
import html
import json
import re
import sys
import time
import unicodedata
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "data" / "KEYWORD_INVENTORY.csv"
OUTPUT = ROOT / "data" / "RECOVERY_004_CANDIDATES.csv"
HEADERS = ["id", "keyword", "category", "source_index", "source_year",
           "source_title", "source_authors", "source_url", "match_location",
           "classification", "review_note"]

def norm(value):
    value = unicodedata.normalize("NFKC", html.unescape(str(value or ""))).lower()
    value = re.sub(r"<[^>]*>", " ", value)
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", value)).strip()

def phrase_in(term, text):
    key = norm(term)
    src = norm(text)
    return bool(key and (" " + key + " ") in (" " + src + " "))

def request_json(url):
    req = Request(url, headers={
        "User-Agent": "AI-Keyword-Historical-Registry/2.0 (public scholarly metadata research)",
        "Accept": "application/json",
    })
    for attempt in range(4):
        try:
            with urlopen(req, timeout=30) as response:
                return json.load(response)
        except HTTPError as error:
            if error.code not in (429, 500, 502, 503, 504):
                raise
            if attempt == 3:
                raise
        except (URLError, TimeoutError):
            if attempt == 3:
                raise
        time.sleep(2 * (attempt + 1))
    return {}

def crossref_year(record):
    years = []
    for name in ("published", "published-online", "published-print", "issued"):
        parts = (record.get(name) or {}).get("date-parts") or []
        if parts and parts[0] and isinstance(parts[0][0], int):
            years.append(parts[0][0])
    return min((y for y in years if 1800 <= y <= 2026), default=None)

def crossref(term):
    # A previously used title-only filter misses relevant abstracts.
    query = urlencode({
        "query.bibliographic": term, "rows": 70,
        "select": "DOI,title,abstract,author,published,published-online,published-print,issued",
    })
    data = request_json("https://api.crossref.org/works?" + query)
    findings = []
    for item in data.get("message", {}).get("items", []):
        title = (item.get("title") or [""])[0]
        abstract = item.get("abstract") or ""
        location = "title" if phrase_in(term, title) else (
            "abstract" if phrase_in(term, abstract) else "")
        if not location:
            continue
        year = crossref_year(item)
        doi = item.get("DOI")
        if year is None or not doi:
            continue
        authors = "; ".join(
            (a.get("given", "") + " " + a.get("family", "")).strip()
            for a in item.get("author", [])[:4]
        )
        findings.append([year, "Crossref", title, authors,
                         "https://doi.org/" + doi, location])
    return findings

def restore_abstract(index):
    if not isinstance(index, dict):
        return ""
    tokens = {}
    for word, positions in index.items():
        for i in positions:
            tokens[i] = word
    return " ".join(tokens[k] for k in sorted(tokens))

def openalex(term):
    # Sort the search window chronologically instead of just selecting
    # the oldest result from a relevance-ranked first page.
    query = urlencode({
        "search.title_and_abstract.exact": '"' + term + '"',
        "sort": "publication_date:asc",
        "per_page": 75,
        "select": "id,title,publication_year,doi,authorships,abstract_inverted_index",
    })
    data = request_json("https://api.openalex.org/works?" + query)
    findings = []
    for item in data.get("results", []):
        title = item.get("title") or ""
        abstract = restore_abstract(item.get("abstract_inverted_index"))
        location = "title" if phrase_in(term, title) else (
            "abstract" if phrase_in(term, abstract) else "")
        if not location:
            continue
        year = item.get("publication_year")
        if not isinstance(year, int) or not 1800 <= year <= 2026:
            continue
        link = item.get("doi") or item.get("id")
        if not link or not link.startswith("https://"):
            continue
        authors = "; ".join((x.get("author") or {}).get("display_name", "")
                            for x in item.get("authorships", [])[:4])
        findings.append([year, "OpenAlex", title, authors, link, location])
    return findings

def examine(item):
    key = item["id"]
    term = item["keyword"]
    errors = []
    proposals = []
    for index_name, fn in (("Crossref", crossref), ("OpenAlex", openalex)):
        try:
            proposals.extend(fn(term))
        except Exception as error:
            errors.append(index_name + ": " + type(error).__name__ + " " + str(error)[:120])
    proposals.sort(key=lambda row: (row[0], 0 if row[5] == "title" else 1))
    seen = set()
    unique = []
    for year, index, title, authors, link, location in proposals:
        key2 = link.lower()
        if key2 in seen:
            continue
        seen.add(key2)
        unique.append({
            "id": key, "keyword": term, "category": item["field"],
            "source_index": index, "source_year": year, "source_title": title,
            "source_authors": authors, "source_url": link,
            "match_location": location,
            "classification": "candidate_exact_phrase_attestation_NOT_verified_origin",
            "review_note": "Found in dated metadata; check original context, term meaning, earlier works, and whether the source uses the exact AI-related sense.",
        })
        if len(unique) == 5:
            break
    if not unique:
        unique.append({
            "id": key, "keyword": term, "category": item["field"],
            "source_index": "", "source_year": "", "source_title": "",
            "source_authors": "", "source_url": "", "match_location": "",
            "classification": "no_candidate_or_search_failure",
            "review_note": "; ".join(errors) if errors else
            "No exact phrase in searched title/abstract windows. Search full text, books, documentation, variants, predecessor methods.",
        })
    return unique

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, default=100,
                        help="Number of pending records to query; default 100, max 1000")
    parser.add_argument("--workers", type=int, default=3, help="1-6 concurrent record queries")
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    if not 1 <= args.limit <= 1000 or not 1 <= args.workers <= 6:
        parser.error("--limit must be 1-1000 and --workers must be 1-6")
    with MASTER.open(encoding="utf-8-sig", newline="") as fh:
        inventory = list(csv.DictReader(fh))
    if len(inventory) != 20100 or len({r["id"] for r in inventory}) != 20100:
        raise ValueError("Inventory changed or duplicate IDs; refuse research")
    pending = sorted(
        (r for r in inventory if r.get("recovery_batch") == "004_pending_recheck"
         and not r.get("historical_date")), key=lambda r: r["id"]
    )[:args.limit]
    if not pending:
        print("No selected undated entries remain.")
        return
    all_results = {}
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        jobs = {pool.submit(examine, row): row["id"] for row in pending}
        for num, done in enumerate(as_completed(jobs), 1):
            all_results[jobs[done]] = done.result()
            if num % 20 == 0 or num == len(pending):
                print(f"Examined {num}/{len(pending)}", flush=True)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as fh:
        out = csv.DictWriter(fh, fieldnames=HEADERS)
        out.writeheader()
        for row in pending:
            out.writerows(all_results[row["id"]])
    sourced = sum(any(x["source_year"] for x in all_results[row["id"]])
                  for row in pending)
    print(json.dumps({
        "records_queried": len(pending),
        "records_with_dated_candidates": sourced,
        "records_without_candidates": len(pending) - sourced,
        "source_candidates_not_verified_first_use": True,
        "inventory_modified": False,
        "output": str(args.output)
    }, indent=2))

if __name__ == "__main__":
    main()
