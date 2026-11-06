#!/usr/bin/env python3
"""Document dated source attestations for AIH-01501 through AIH-02500.

Never claim first-ever term use from a scholarly title match.
Historical first-use stays blank until a proper primary-source origin audit.
"""
import csv, json, time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import Counter

from research_dates_first_500 import lookup as crossref_lookup
from research_dates_openalex_fallback import look as openalex_lookup

ROOT=Path(__file__).resolve().parents[1]
FILE=ROOT/"data/KEYWORD_INVENTORY.csv"
INDEX=ROOT/"batches/DATE_RESEARCH_003_NEXT_1000.md"
PAGES=ROOT/"batches/date-research-002"
REPORT=ROOT/"data/DATE_RESEARCH_003_REPORT.json"

def safe(value):
    return str(value or "").replace("|"," / ").replace("\n"," ").strip()

def run_queries(candidates, func, workers, label):
    results={}
    if not candidates:return results
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures={pool.submit(func, r["keyword"]):r["id"] for r in candidates}
        for n,future in enumerate(as_completed(futures),1):
            uid=futures[future]
            try:results[uid]=future.result()
            except Exception as e:
                results[uid]=None
            if n%100==0 or n==len(candidates):
                print(label, n,"/",len(candidates),flush=True)
    return results

def main():
    with FILE.open(encoding="utf-8-sig",newline="") as f:
        reader=csv.DictReader(f)
        columns=list(reader.fieldnames or [])
        all_rows=list(reader)
    assert len(all_rows)==20100
    assert len({r["id"] for r in all_rows})==20100
    selected=sorted((r for r in all_rows if 1501<=int(r["id"].split("-")[1])<=2500),
                    key=lambda r:r["id"])
    assert len(selected)==1000
    assert selected[0]["id"]=="AIH-01501" and selected[-1]["id"]=="AIH-02500"
    fields=["historical_evidence_date","historical_evidence_type","historical_evidence_title",
            "historical_evidence_url","historical_evidence_authors","historical_evidence_notes"]
    for field in fields:
        if field not in columns:columns.append(field)
    # Never modify the previously completed first-1500 records.
    earlier=[r.copy() for r in all_rows if int(r["id"].split("-")[1])<=1500]
    assert all(not r.get("first_use_date") for r in selected)

    todo=[r for r in selected if not r.get("historical_evidence_date")]
    print("Crossref first-pass requests:",len(todo),flush=True)
    crossref=run_queries(todo,crossref_lookup,14,"Crossref")
    count_crossref=0
    for r in todo:
        result=crossref.get(r["id"])
        if result and len(result)==6:
            r.update(zip(fields,result))
            if result[0]:count_crossref+=1
        else:
            r.update(zip(fields,("","search_error","","","","Crossref request failed")))
    pending=[r for r in selected if not r.get("historical_evidence_date")]
    print("OpenAlex second-pass requests:",len(pending),flush=True)
    openalex=run_queries(pending,openalex_lookup,9,"OpenAlex")
    count_openalex=0
    for r in pending:
        result=openalex.get(r["id"])
        if result and len(result)==6 and result[0]:
            r.update(zip(fields,result))
            count_openalex+=1

    assert all(not r.get("first_use_date") for r in selected)
    prior=[r for r in all_rows if int(r["id"].split("-")[1])<=1500]
    assert prior==earlier
    # Write once, only after all sources have been queried and IDs validated.
    with FILE.open("w",newline="",encoding="utf-8") as f:
        writer=csv.DictWriter(f,fieldnames=columns,lineterminator="\n")
        writer.writeheader()
        writer.writerows(all_rows)

    PAGES.mkdir(parents=True,exist_ok=True)
    index=[
        "# Date Research 003 — Next 1,000 AI Keywords",
        "",
        "All 1,000 permanent records (AIH-01501–AIH-02500) are listed in the **two complete 500-row tables** linked below.",
        "",
        "The date is the date of a *documented source using the term*, not independently established original or earliest-ever terminology. A found paper is not necessarily the first paper.",
        "",
        "The true first-use date remains blank until independently confirmed. Unresolved rows display an em dash.",
        "",
        "| Page | IDs | Entries | Complete research table |",
        "|---:|---|---:|---|",
    ]
    for i in range(2):
        chunk=selected[i*500:(i+1)*500]
        first,last=chunk[0]["id"],chunk[-1]["id"]
        page=f"page-{i+1:02d}.md"
        index.append(f"| {i+1} | {first}–{last} | 500 | [View all 500](date-research-003/{page}) |")
        lines=[
            f"# Date Research 003 — Page {i+1}/2",
            "",
            f"**500 keywords:** {first} to {last}. Original first-use dates are NOT yet established.",
            "",
            "[Back to research index](../DATE_RESEARCH_003_NEXT_1000.md) · [Complete inventory](../../data/KEYWORD_INVENTORY.csv)",
            "",
            "| ID | Keyword | Category | Source-documented date | Source | Evidence classification |",
            "|---|---|---|---|---|---|",
        ]
        for r in chunk:
            typ=r.get("historical_evidence_type") or "unresolved"
            status={
              "crossref_exact_title_attestation":"Crossref exact-title match",
              "openalex_exact_title_attestation":"OpenAlex exact-title match",
              "unresolved":"No dated title found",
              "search_error":"Search incomplete",
            }.get(typ,safe(typ))
            url=r.get("historical_evidence_url")
            evidence=("[Publication]("+url+")" if url else "—")
            lines.append("| "+" | ".join([
                safe(r["id"]),safe(r["keyword"]),safe(r["field"]),
                safe(r.get("historical_evidence_date")) or "—",
                evidence,status
            ])+" |")
        lines+=["","*Source date is not proof of first use. Use the evidence link to inspect the publication.*",""]
        (PAGES/page).write_text("\n".join(lines)+"\n",encoding="utf-8")

    stats=Counter(r.get("historical_evidence_type") for r in selected)
    dated=sum(bool(r.get("historical_evidence_date")) for r in selected)
    report={
        "batch":"DATE_RESEARCH_003",
        "id_range":["AIH-01501","AIH-02500"],
        "examined":1000,
        "dated_source_records":dated,
        "crossref_title_matches":stats["crossref_exact_title_attestation"],
        "openalex_title_matches":stats["openalex_exact_title_attestation"],
        "unresolved":1000-dated,
        "verified_original_first_use":0,
        "all_ids_preserved":True,
        "previous_1500_unchanged":True,
        "inventory_size":len(all_rows),
        "note":"Exact-title scholarly citation dates, NOT proven first-ever phrase use."
    }
    REPORT.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    index+=["","## Research quality summary","",
            "| Metric | Count |","|---|---:|",
            "| Keywords reviewed | 1,000 |",
            f"| Source-documented dates | {dated} |",
            f"| Crossref exact-title matches | {stats['crossref_exact_title_attestation']} |",
            f"| OpenAlex exact-title matches | {stats['openalex_exact_title_attestation']} |",
            f"| No linked source date | {1000-dated} |",
            "| Conclusively verified first-ever wording dates | 0 |",
            "",
            "[Audit report JSON](../data/DATE_RESEARCH_003_REPORT.json) · [Master keyword inventory](../data/KEYWORD_INVENTORY.csv)",
            "",
            "**Historical limitation:** Scholarly indexes return relevance-ranked works, not comprehensive chronological term histories. Further checking against original papers and earlier occurrences is needed."
            ]
    INDEX.write_text("\n".join(index)+"\n",encoding="utf-8")
    for i in range(1,3):
        count=sum(x.startswith("| AIH-") for x in (PAGES/f"page-{i:02d}.md").read_text(encoding="utf-8").splitlines())
        assert count==500
    print("FINAL "+json.dumps(report),flush=True)

if __name__=="__main__":main()
