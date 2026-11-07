#!/usr/bin/env python3
"""Semantic audit: replace weak Batch 010 matches with four original technical sources.

Provenance distinction: dated original method/concept publication != the first
historical use of the modern keyword string or a complete origin proof.
"""
import csv,json,re
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MASTER=ROOT/"data/KEYWORD_INVENTORY.csv"
REPORT=ROOT/"data/DATE_RESEARCH_010_REPORT.json"
INDEX=ROOT/"batches/DATE_RESEARCH_010_NEXT_2000.md"
PAGES=ROOT/"batches/date-research-010"
FIX=[
 ("AIH-12518","mapreduce frameworks","2004","primary_mapreduce_technical_paper",
  "MapReduce: Simplified Data Processing on Large Clusters",
  "https://www.usenix.org/conference/osdi-04/mapreduce-simplified-data-processing-large-clusters",
  "Jeffrey Dean; Sanjay Ghemawat",
  "Original 2004 OSDI publication describing the MapReduce computational model and runtime. The term 'MapReduce frameworks' as a plural label may have been adopted later."),
 ("AIH-13101","active contours","1988","primary_computer_vision_method_paper",
  "Snakes: Active Contour Models",
  "https://doi.org/10.1007/BF00133570",
  "Michael Kass; Andrew Witkin; Demetri Terzopoulos",
  "1988 International Journal of Computer Vision original snakes/active contour model publication. Earlier uses of 'contour' or other active methods do not equal this named method."),
 ("AIH-13501","bp algorithm","1986","early_neural_backpropagation_paper",
  "Learning representations by back-propagating errors",
  "https://doi.org/10.1038/323533a0",
  "David E. Rumelhart; Geoffrey E. Hinton; Ronald J. Williams",
  "1986 influential back-propagation paper in neural-network training. 'BP algorithm' is ambiguous and may refer to belief propagation; this is a category-grounded source anchor, NOT the first invented backpropagation or the first use of BP abbreviation."),
 ("AIH-14500","model view controller pattern","1979","early_original_mvc_technical_note",
  "Models–Views–Controllers",
  "https://zenodo.org/records/3676092",
  "Trygve Reenskaug",
  "Original December 10, 1979 Xerox PARC MVC technical note, archived on Zenodo. MVC idea was conceived in 1978; 'pattern' as later terminology may postdate the note."),
]
def main():
    with MASTER.open(encoding="utf-8-sig",newline="") as f:
        rd=csv.DictReader(f);fields=list(rd.fieldnames);rows=list(rd)
    assert len(rows)==20100 and len({r["id"] for r in rows})==20100
    lookup={r["id"]:r for r in rows}
    audit=[]
    for uid,keyword,year,typ,title,url,authors,notes in FIX:
        r=lookup[uid]
        assert r["keyword"]==keyword and not r.get("first_use_date")
        assert 12501<=int(uid.split("-")[-1])<=14500
        prev={"date":r.get("historical_evidence_date",""),
              "estimated":r.get("estimated_first_use_year",""),
              "source":r.get("historical_evidence_url") or r.get("estimated_source_url")}
        r["historical_evidence_date"]=year
        r["historical_evidence_type"]=typ
        r["historical_evidence_title"]=title
        r["historical_evidence_url"]=url
        r["historical_evidence_authors"]=authors
        r["historical_evidence_notes"]=notes
        for field in ("estimated_first_use_year","estimated_source_url","estimated_source_title","estimated_reason","estimated_confidence"):
            r[field]=""
        r["date_status"]="documented_source_not_first_use"
        r["display_date"]=year
        audit.append({"id":uid,"keyword":keyword,"previous":prev,"documented_source_year":year,
                      "source_url":url,"notes":notes})
    group=[r for r in rows if 12501<=int(r["id"].split("-")[-1])<=14500]
    counts=Counter(r["date_status"] for r in group)
    assert len(group)==2000 and sum(counts.values())==2000
    assert set(counts)<=set(["documented_source_not_first_use","estimated_star","unresolved"])
    for x in group:
        if x["date_status"]=="estimated_star":
            assert x["display_date"].endswith(" ★") and x["estimated_reason"] and x["estimated_source_url"]
    with MASTER.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields,lineterminator="\n")
        w.writeheader();w.writerows(rows)
    observed=set()
    for page in sorted(PAGES.glob("page-*.md")):
        lines=page.read_text(encoding="utf-8").splitlines()
        for i,line in enumerate(lines):
            if not line.startswith("| AIH-"):continue
            uid=line.split("|")[1].strip()
            if uid not in {x[0] for x in FIX}:continue
            observed.add(uid)
            r=lookup[uid]
            lines[i]="| "+" | ".join([uid,r["keyword"],r["field"],r["historical_evidence_date"],
                 "Original/early method source (first term use unverified)",
                 "[Source]("+r["historical_evidence_url"]+")"])+" |"
        assert sum(x.startswith("| AIH-") for x in lines)==500
        page.write_text("\n".join(lines)+"\n",encoding="utf-8")
    assert observed=={x[0] for x in FIX}
    report=json.loads(REPORT.read_text(encoding="utf-8"))
    assert report["examined"]==2000
    report.update(documented_source_dates=counts["documented_source_not_first_use"],
                  estimated_star_dates=counts["estimated_star"],
                  unresolved=counts["unresolved"],
                  dated_or_estimated=counts["documented_source_not_first_use"]+counts["estimated_star"],
                  manual_original_source_corrections=len(FIX),manual_source_audit=audit)
    REPORT.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    text=INDEX.read_text(encoding="utf-8")
    for title,count in (("Linked publication dates",counts["documented_source_not_first_use"]),
                        ("Estimated years ★",counts["estimated_star"]),
                        ("Unresolved",counts["unresolved"])):
        text=re.sub(r"(\| "+re.escape(title)+r" \| )\d+( \|)",lambda m:m.group(1)+str(count)+m.group(2),text)
    if "## Manual primary-source checks" not in text:
        text+="\n## Manual primary-source checks\n\n"
        text+="Four technical method dates were checked against original/early papers, without claiming the first historical occurrence of the exact term.\n\n"
        for item in audit:
            text+=f"- **{item['id']} {item['keyword']}** — {item['documented_source_year']}, [source]({item['source_url']}). {item['notes']}\n"
    INDEX.write_text(text,encoding="utf-8")
    print(json.dumps({"manual_source_checks":len(FIX),"documented":counts["documented_source_not_first_use"],
          "estimates_star":counts["estimated_star"],"unresolved":counts["unresolved"]}))
if __name__=="__main__":
    main()
