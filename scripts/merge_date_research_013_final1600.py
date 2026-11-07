#!/usr/bin/env python3
"""Merge the final 1,600 dated scholarly searches, with starred source-based estimates."""
import csv,json,re
from pathlib import Path
from collections import Counter
ROOT=Path(__file__).resolve().parents[1]
MASTER=ROOT/"data/KEYWORD_INVENTORY.csv"
REPORT=ROOT/"data/DATE_RESEARCH_013_REPORT.json"
INDEX=ROOT/"batches/DATE_RESEARCH_013_FINAL_1600.md"
PAGES=ROOT/"batches/date-research-013"
STAGING=ROOT/"data/date_staging"
NEW_FIELDS=["historical_evidence_date","historical_evidence_type","historical_evidence_title",
"historical_evidence_url","historical_evidence_authors","historical_evidence_notes",
"estimated_first_use_year","estimated_source_url","estimated_source_title",
"estimated_reason","estimated_confidence","date_status","display_date"]
def clean(x):return str(x or "").replace("|"," / ").replace("\n"," ").strip()
def main():
    patches=[]
    for start in (18501,19501):
        path=STAGING/f"segment_date_013_{start:05d}.json"
        p=json.loads(path.read_text(encoding="utf-8"))
        expected=min(1000,20101-start)
        assert p["start"]==start and p["end"]==min(20100,start+999) and len(p["results"])==expected
        patches+=p["results"]
    by_id={p["id"]:p for p in patches}
    assert len(by_id)==1600
    assert set(by_id)=={f"AIH-{i:05d}" for i in range(18501,20101)}
    with MASTER.open(encoding="utf-8-sig",newline="") as f:
        reader=csv.DictReader(f);cols=list(reader.fieldnames);all_rows=list(reader)
    assert len(all_rows)==20100
    assert len({r["id"] for r in all_rows})==20100
    old={r["id"]:r.copy() for r in all_rows if int(r["id"].split("-")[-1])<=18500}
    for field in NEW_FIELDS:
        if field not in cols:cols.append(field)
    tally=Counter();changed=[]
    for row in all_rows:
        p=by_id.get(row["id"])
        if p is None:continue
        assert not row.get("first_use_date") and not row.get("historical_evidence_date")
        evidence=p.get("evidence");estimate=p.get("estimate")
        assert not (evidence and estimate)
        if evidence:
            y=evidence["historical_evidence_date"]
            assert re.fullmatch(r"(18|19|20)\d\d",y)
            row.update(evidence)
            row["date_status"]="documented_source_not_first_use"
            row["display_date"]=y
            tally["documented_source_dates"]+=1
        elif estimate:
            y=estimate["estimated_first_use_year"]
            assert re.fullmatch(r"(18|19|20)\d\d",y)
            assert estimate["estimated_source_url"].startswith("https://")
            assert estimate.get("estimated_reason")
            row.update(estimate)
            row["date_status"]="estimated_star"
            row["display_date"]=y+" ★"
            tally["estimated_star_dates"]+=1
        else:
            row["date_status"]="unresolved"
            row["display_date"]=""
            row["historical_evidence_type"]="search_error" if p.get("crossref_error") or p.get("openalex_error") else "unresolved"
            tally["unresolved"]+=1
        assert not row.get("first_use_date")
        changed.append(row)
    changed.sort(key=lambda r:r["id"])
    assert len(changed)==1600 and sum(tally.values())==1600
    assert all(r==old[r["id"]] for r in all_rows if r["id"] in old)
    for row in changed:
        if row["date_status"]=="estimated_star":
            assert row["display_date"].endswith(" ★") and row["estimated_reason"] and row["estimated_source_url"]
            assert not row.get("historical_evidence_date")
        if row["date_status"]=="documented_source_not_first_use":
            assert row["historical_evidence_url"] and "★" not in row["display_date"]
    with MASTER.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=cols,lineterminator="\n")
        w.writeheader();w.writerows(all_rows)
    PAGES.mkdir(parents=True,exist_ok=True)
    index=[
       "# Date Research 013 — Final 1,600 Keywords","",
       "Complete 1,600 permanent IDs: AIH-18501–AIH-20100. Three 500-row tables plus one 100-row table.","",
       "**Date legend:** Unstarred dates refer to documented publications, not verified term coinage. **★** denotes an estimated historical year inferred from related scholarly research, always low confidence. — means unresolved.","",
       "All first-use dates remain unverified. Existing 18,500 previously researched IDs were not modified.","",
       "| Page | ID range | Keywords | Full table |","|---:|---|---:|---|"
    ]
    for i in range(4):
        block=changed[i*500:(i+1)*500]
        page=f"page-{i+1:02d}.md"
        index.append(f"| {i+1} | {block[0]['id']}–{block[-1]['id']} | {len(block)} | [Open table](date-research-013/{page}) |")
        lines=[
          f"# Date Research 013 — Table {i+1}/4","",
          f"{len(block)} keywords: {block[0]['id']} through {block[-1]['id']}.","",
          "[Back to index](../DATE_RESEARCH_013_FINAL_1600.md) | [Master database](../../data/KEYWORD_INVENTORY.csv)","",
          "**★ means an estimated year, not the first verified historical use.**","",
          "| ID | Keyword | Category | Date | Classification | Source |",
          "|---|---|---|---|---|---|"]
        for row in block:
            if row["date_status"]=="estimated_star":
                label="Estimated ★ (low confidence)"
                source=row["estimated_source_url"]
            elif row["date_status"]=="documented_source_not_first_use":
                label="Dated publication mention"
                source=row["historical_evidence_url"]
            else:label="Unresolved";source=""
            lines.append("| "+" | ".join([
               row["id"],clean(row["keyword"]),clean(row["field"]),
               clean(row["display_date"]) or "—",label,
               ("[Source]("+source+")" if source else "—")
            ])+" |")
        lines+=["","**Date caveat:** Dated sources establish documented use, not origin. Estimations are from related papers and are flagged ★.","",
                "Reasoning and source titles for estimates are stored in the master CSV."]
        (PAGES/page).write_text("\n".join(lines)+"\n",encoding="utf-8")
        assert sum(s.startswith("| AIH-") for s in lines)==len(block)
    index+=["","## Results","","| Measure | Count |","|---|---:|",
            "| Keywords processed | 1,600 |",
            f"| Linked publication dates | {tally['documented_source_dates']} |",
            f"| Estimated years ★ | {tally['estimated_star_dates']} |",
            f"| Unresolved | {tally['unresolved']} |",
            "| Verified earliest term-use dates | 0 |","",
            "[Research report](../data/DATE_RESEARCH_013_REPORT.json) | [Master CSV](../data/KEYWORD_INVENTORY.csv)",""]
    INDEX.write_text("\n".join(index)+"\n",encoding="utf-8")
    report={"batch":"DATE_RESEARCH_013","range":["AIH-18501","AIH-20100"],
            "examined":1600,**{k:tally[k] for k in ("documented_source_dates","estimated_star_dates","unresolved")},
            "dated_or_estimated":tally["documented_source_dates"]+tally["estimated_star_dates"],
            "verified_original_first_use":0,"existing_first_18500_unchanged":True,
            "stable_ids_preserved":True,"inventory_total":20100,
            "estimated_display_rule":"★ immediately after year; low-confidence supporting source and reasoning mandatory.",
            "note":"Neither linked publication dates nor estimated years prove historical first use."}
    REPORT.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("COMPLETE "+json.dumps(report,ensure_ascii=False),flush=True)
if __name__=="__main__":main()
