#!/usr/bin/env python3
"""Sort all 20,100 permanent IDs by available year while retaining evidence grades."""
import csv,json,re
from pathlib import Path
from collections import Counter
ROOT=Path(__file__).resolve().parents[1]
DIR=ROOT/"chronology"
PAGES=DIR/"pages"
REPORT=ROOT/"data/FINAL_COVERAGE_20100_REPORT.json"
def clean(value):
    return str(value or "").strip().replace("|"," / ").replace("\n"," ").replace("\r"," ")
def year(value):
    match=re.search(r"(1[0-9]{3}|20[0-9]{2})",str(value or ""))
    return int(match.group(1)) if match else None
def classify(r):
    fields=(
        ("first_use_date","first_use_field","Recorded first use (not independently verified)","",0,""),
        ("historical_evidence_date","source_dated","Dated publication (not proven term origin)","historical_evidence_url",1,""),
        ("estimated_first_use_year","star_estimate","Estimated ★, related scholarly evidence","estimated_source_url",2," ★"),
        ("guessed_first_use_year","double_star_guess","Speculative ★★, no direct evidence","",3," ★★")
    )
    for field,status,label,urlfield,priority,suffix in fields:
        value=clean(r.get(field))
        if value and year(value):
            y=year(value)
            return {"year":y,"display":str(y)+suffix,"status":status,
                    "label":label,"url":clean(r.get(urlfield)) if urlfield else "","priority":priority}
    return {"year":None,"display":"—","status":"undated","label":"Unresolved","url":"","priority":4}
def main():
    with (ROOT/"data/KEYWORD_INVENTORY.csv").open(newline="",encoding="utf-8-sig") as f:
        records=list(csv.DictReader(f))
    assert len(records)==20100
    ids={r["id"] for r in records}
    assert ids=={f"AIH-{n:05d}" for n in range(1,20101)}
    rows=[(r,classify(r)) for r in records]
    counts=Counter(v["status"] for _,v in rows)
    assert sum(counts.values())==20100
    rows.sort(key=lambda pair:(
        pair[1]["year"] if pair[1]["year"] is not None else 99999,
        pair[1]["priority"],clean(pair[0]["keyword"]).casefold(),pair[0]["id"]))
    PAGES.mkdir(parents=True,exist_ok=True)
    page_count=(len(rows)+499)//500
    assert page_count==41
    index=[
        "# Complete Chronological Index — 20,100 AI/CS Keywords","",
        "All permanent AIH identifiers retained. Entries sorted oldest to newest, with undated terms at the end.",
        "",
        "**Evidence:** Unstarred source years mean a dated publication or milestone, NOT proven first-ever term usage. "
        "**★** means an inferred low-confidence year with related source. "
        "**★★** means a speculative historical-era guess without direct evidence. "
        "An em dash indicates no usable date.",
        "",
        "[Original master CSV](../data/KEYWORD_INVENTORY.csv) | [Coverage audit](../data/FINAL_COVERAGE_20100_REPORT.json)",
        "","## Coverage summary","","| Status | Entries |","|---|---:|",
        f"| Dated publication attestations | {counts['source_dated']:,} |",
        f"| Estimates ★ | {counts['star_estimate']:,} |",
        f"| Speculative placeholders ★★ | {counts['double_star_guess']:,} |",
        f"| No year | {counts['undated']:,} |",
        f"| Recorded first-use field, independent verification pending | {counts['first_use_field']:,} |",
        "| **Total** | **20,100** |",
        "","## All chronological pages","","| Page | Year range | Records | Link |",
        "|---:|---|---:|---|"
    ]
    seen=set()
    sizes=[]
    for i,start in enumerate(range(0,len(rows),500),1):
        batch=rows[start:start+500]
        sizes.append(len(batch))
        def label(meta):
            return str(meta["year"]) if meta["year"] is not None else "Undated"
        left,right=label(batch[0][1]),label(batch[-1][1])
        span=left if left==right else left+" – "+right
        name=f"page-{i:02d}.md"
        index.append(f"| {i:02d} | {span} | {len(batch)} | [Open table](pages/{name}) |")
        lines=[
            f"# Chronological Keywords — Page {i:02d}/41","",
            f"{len(batch)} records from {span}. Original IDs unchanged.","",
            "[Full chronology](../README.md) | [Master inventory](../../data/KEYWORD_INVENTORY.csv)","",
            "Unstarred source years are not verified first usages; ★ inferred; ★★ speculative.","",
            "| ID | Keyword | Field | Year | Evidence | Reference |",
            "|---|---|---|---|---|---|"
        ]
        for r,meta in batch:
            assert r["id"] not in seen
            seen.add(r["id"])
            link=f"[Source]({meta['url']})" if meta["url"].startswith(("https://","http://")) else "—"
            lines.append("| "+" | ".join([
                r["id"],clean(r["keyword"]),clean(r["field"]),
                meta["display"],meta["label"],link])+" |")
        (PAGES/name).write_text("\n".join(lines)+"\n",encoding="utf-8")
        assert sum(l.startswith("| AIH-") for l in lines)==len(batch)
    assert seen==ids and sizes==[500]*40+[100]
    index.extend(["","## Important limitations","",
                  "This index is a chronological research navigator, NOT a validated timeline of original word coinage. "
                  "Original first uses and AI-specific senses require separate examination of early primary sources. "
                  "The inventory also contains broader CS and potentially misclassified terminology.",""])
    (DIR/"README.md").write_text("\n".join(index)+"\n",encoding="utf-8")
    result={
        "inventory_total":20100,"all_ids_unique_and_complete":True,
        "range":["AIH-00001","AIH-20100"],
        "consecutive_research_batch_coverage_complete":True,
        "chronology_pages":41,"chronology_page_sizes":sizes,
        "source_dated_publication_attestations":counts["source_dated"],
        "estimated_years_star":counts["star_estimate"],
        "speculative_years_double_star":counts["double_star_guess"],
        "entries_without_usable_year":counts["undated"],
        "first_use_field_populated_but_unverified":counts["first_use_field"],
        "fully_verified_first_uses":0,
        "caveat":"A publication mention is not confirmed earliest term use. ★ inferred, ★★ speculative.",
        "remaining_research":"Manually verify original term usage, unresolved records, and category relevance."
    }
    REPORT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in result.items() if k in (
       "inventory_total","chronology_pages","source_dated_publication_attestations",
       "estimated_years_star","speculative_years_double_star","entries_without_usable_year")},indent=2))
if __name__=="__main__":main()
