#!/usr/bin/env python3
"""Correct high-value dates in Batch 011 to early original technical publications.

Source-paper dates are not represented as first-ever lexical coinages.
Preserve all prior work and speculative double-star dates on older records.
"""
import csv,json,re
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MASTER=ROOT/"data/KEYWORD_INVENTORY.csv"
REPORT=ROOT/"data/DATE_RESEARCH_011_REPORT.json"
INDEX=ROOT/"batches/DATE_RESEARCH_011_NEXT_2000.md"
PAGES=ROOT/"batches/date-research-011"
FIX=[
 ("AIH-14501","model view controller","1979","original_mvc_technical_note",
  "Models–Views–Controllers",
  "https://zenodo.org/records/3676092",
  "Trygve Reenskaug",
  "Original December 1979 Xerox PARC MVC technical note. MVC idea existed in 1978; the original note is an early documented method source, not proven earliest wording."),
 ("AIH-15481","mamdani","1975","primary_fuzzy_controller_paper",
  "An experiment in linguistic synthesis with a fuzzy logic controller",
  "https://doi.org/10.1016/S0020-7373(75)80002-2",
  "E. H. Mamdani; S. Assilian",
  "January 1975 original fuzzy linguistic controller paper. The later use of the eponym 'Mamdani' for a fuzzy inference type is not proven to originate in 1975."),
 ("AIH-15691","border gateway protocol","1989","original_internet_protocol_specification",
  "A Border Gateway Protocol (BGP), RFC 1105",
  "https://www.rfc-editor.org/info/rfc1105",
  "Kirk Lougheed; Yakov Rekhter",
  "June 1989 RFC 1105 original BGP protocol specification. This is an early primary-source occurrence, not independently certified first-ever naming."),
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
        assert 14501<=int(uid.split("-")[-1])<=16500
        prior={"source_year":r.get("historical_evidence_date",""),
               "estimated_year":r.get("estimated_first_use_year",""),
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
        audit.append({"id":uid,"keyword":keyword,"previous":prior,"source_year":year,
                      "source_url":url,"notes":notes})
    group=[r for r in rows if 14501<=int(r["id"].split("-")[-1])<=16500]
    counts=Counter(r["date_status"] for r in group)
    assert len(group)==2000 and set(counts)<=set(["documented_source_not_first_use","estimated_star","unresolved"])
    assert sum(counts.values())==2000
    with MASTER.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields,lineterminator="\n")
        w.writeheader();w.writerows(rows)
    seen=set()
    for i in range(1,5):
        path=PAGES/f"page-{i:02d}.md"
        lines=path.read_text(encoding="utf-8").splitlines()
        for idx,line in enumerate(lines):
            if not line.startswith("| AIH-"):continue
            uid=line.split("|")[1].strip()
            if uid not in {x[0] for x in FIX}:continue
            seen.add(uid)
            r=lookup[uid]
            lines[idx]="| "+" | ".join([
                uid,r["keyword"],r["field"],r["historical_evidence_date"],
                "Original/early method source (first exact use unverified)",
                "[Source]("+r["historical_evidence_url"]+")"])+" |"
        assert sum(x.startswith("| AIH-") for x in lines)==500
        path.write_text("\n".join(lines)+"\n",encoding="utf-8")
    assert seen=={x[0] for x in FIX}
    report=json.loads(REPORT.read_text(encoding="utf-8"))
    assert report["examined"]==2000 and report["inventory_total"]==20100
    report.update(documented_source_dates=counts["documented_source_not_first_use"],
                  estimated_star_dates=counts["estimated_star"],
                  unresolved=counts["unresolved"],
                  dated_or_estimated=counts["documented_source_not_first_use"]+counts["estimated_star"],
                  manual_original_source_checks=len(FIX),manual_source_audit=audit)
    REPORT.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    text=INDEX.read_text(encoding="utf-8")
    for title,num in (("Linked publication dates",counts["documented_source_not_first_use"]),
                      ("Estimated years ★",counts["estimated_star"]),
                      ("Unresolved",counts["unresolved"])):
        text=re.sub(r"(\| "+re.escape(title)+r" \| )\d+( \|)",lambda m:m.group(1)+str(num)+m.group(2),text)
    if "## Manual early-source checks" not in text:
        text+="\n## Manual early-source checks\n\n"
        text+="Three core historical method dates were replaced with earlier original documentation. These dates are not claims of verified first-ever exact wording.\n\n"
        for item in audit:
            text+=f"- **{item['id']} {item['keyword']}** — {item['source_year']}, [primary source]({item['source_url']}). {item['notes']}\n"
    INDEX.write_text(text,encoding="utf-8")
    print(json.dumps({"manually_checked":len(FIX),"documented":counts["documented_source_not_first_use"],
          "estimates_star":counts["estimated_star"],"unresolved":counts["unresolved"]}))
if __name__=="__main__":
    main()
