#!/usr/bin/env python3
"""Second-index evidence pass for first 500 historical keyword records.

Search OpenAlex publications and keep an exact normalized keyword match within
the paper title; preserve prior Crossref and historical research milestone links.
This DOES NOT establish a term's first-ever historical use.
"""
import csv,json,re,time,html,unicodedata
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request,urlopen
from urllib.error import HTTPError
from concurrent.futures import ThreadPoolExecutor,as_completed
from collections import Counter
from research_dates_first_500 import exact_title

root=Path(__file__).resolve().parents[1]
inventory=root/"data/KEYWORD_INVENTORY.csv"
index=root/"batches/DATE_RESEARCH_001_FIRST_500.md"
report=root/"data/DATE_RESEARCH_001_REPORT.json"

def look(term):
    url="https://api.openalex.org/works?"+urlencode({
        "search":term,"per_page":60,
        "select":"id,title,publication_year,doi,authorships"
    })
    req=Request(url,headers={"Accept":"application/json",
        "User-Agent":"AI-Historical-Keyword-Research/1.0"})
    for attempt in range(3):
        try:
            with urlopen(req,timeout=20) as response:result=json.load(response)
            matched=[]
            for item in result.get("results",[]):
                title=item.get("title") or ""
                if not exact_title(term,title):continue
                y=item.get("publication_year")
                if not isinstance(y,int) or not (1800<=y<=2026):continue
                citation=item.get("doi") or item.get("id")
                if not citation or not citation.startswith("https://"):continue
                authors=[(a.get("author") or {}).get("display_name","")
                         for a in item.get("authorships",[])[:3]]
                matched.append((y,title,citation,"; ".join(x for x in authors if x)))
            if not matched:return None
            y,title,citation,authors=min(matched,key=lambda z:(z[0],len(z[1])))
            return (str(y),"openalex_exact_title_attestation",title,citation,authors,
                    "Earliest year among up to 60 OpenAlex relevance-ranked exact-title matches; original first use not demonstrated.")
        except HTTPError as e:
            if attempt<2 and e.code in (429,500,502,503,504):
                time.sleep((attempt+1)*4);continue
            return None
        except Exception:
            if attempt<2:time.sleep(1+attempt);continue
            return None
    return None

def main():
    with inventory.open(encoding="utf-8",newline="") as f:
        reader=csv.DictReader(f);headers=list(reader.fieldnames);records=list(reader)
    target=sorted((r for r in records if int(r["id"].split("-")[-1])<=500),key=lambda r:r["id"])
    assert len(records)==20100 and len(target)==500
    todo=[r for r in target if not r.get("historical_evidence_date")]
    print("Second index lookup unresolved count",len(todo),flush=True)
    findings={}
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures={pool.submit(look,r["keyword"]):r["id"] for r in todo}
        for i,future in enumerate(as_completed(futures),1):
            result=future.result()
            if result:findings[futures[future]]=result
            if i%25==0:print("Examined with second index",i,"of",len(todo),flush=True)
    for r in todo:
        val=findings.get(r["id"])
        if not val:continue
        for field,value in zip(
            ["historical_evidence_date","historical_evidence_type","historical_evidence_title",
             "historical_evidence_url","historical_evidence_authors","historical_evidence_notes"],val):
            r[field]=value
        assert not r.get("first_use_date")
    with inventory.open("w",encoding="utf-8",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=headers,lineterminator="\n")
        writer.writeheader();writer.writerows(records)
    stats=Counter(r["historical_evidence_type"] for r in target)
    dated=sum(bool(r.get("historical_evidence_date")) for r in target)
    body=[
        "# Date Research 001 — 500 AI Keywords",
        "",
        "**All 500 permanent keyword IDs (AIH-00001 through AIH-00500) are included below.**",
        "",
        "These dates are dated primary research milestones or exact mentions in indexed scholarly article titles. They are **not independently verified first-ever use dates**. Research on original terminology is still pending.",
        "",
        "Crossref and OpenAlex results are limited to their relevance-ranked search result windows, so the oldest retrieved title does not necessarily represent the oldest publication anywhere. Search status must not be confused with verified first use.",
        "",
        "| ID | Keyword | Field | Documented source date | Source | Evidence status |",
        "|---|---|---|---|---|---|",
    ]
    for r in target:
        kind=r.get("historical_evidence_type")
        status={
            "legacy_milestone_not_first_use":"Dated research milestone",
            "crossref_exact_title_attestation":"Crossref title match",
            "openalex_exact_title_attestation":"OpenAlex title match",
            "unresolved":"No matching title found",
            "search_error":"Search error / unresolved"
        }.get(kind,"Pending")
        url=r.get("historical_evidence_url")
        link="[Research source]("+url+")" if url else "—"
        body.append("| "+" | ".join([r["id"],r["keyword"].replace("|","/"),
            r["field"].replace("|","/"),r.get("historical_evidence_date") or "—",
            link,status])+" |")
    body+=["","## Results","","| Metric | Count |","|---|---:|",
           "| Keywords covered | 500 |",
           f"| Source-documented dates linked | {dated} |",
           f"| Existing research milestone sources | {stats['legacy_milestone_not_first_use']} |",
           f"| Crossref exact-title records | {stats['crossref_exact_title_attestation']} |",
           f"| OpenAlex additional exact-title records | {stats['openalex_exact_title_attestation']} |",
           f"| Without linked date | {500-dated} |",
           "| Verified first-ever uses of exact words | 0 |",
           "",
           "Do not migrate these dates to first_use_date until historians verify term appearances against earlier scholarly usage.",
           "",
           "[Canonical inventory](../data/KEYWORD_INVENTORY.csv) · [Research report](../data/DATE_RESEARCH_001_REPORT.json)"]
    index.write_text("\n".join(body)+"\n",encoding="utf-8")
    old_report=json.loads(report.read_text(encoding="utf-8"))
    old_report.update({
        "additional_openalex_title_dates":stats["openalex_exact_title_attestation"],
        "additional_crossref_title_dates":stats["crossref_exact_title_attestation"],
        "dated_total":dated,
        "outstanding_no_dated_source":500-dated,
        "verified_original_term_first_uses":0,
        "note":"Document dates do not prove original term coinage."
    })
    report.write_text(json.dumps(old_report,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(old_report,indent=2),flush=True)

if __name__=="__main__":main()
