#!/usr/bin/env python3
"""Batch 013: correct five original/early field-specific citations and withdraw two cross-domain matches.
Do not confuse publication/source dates with the first-ever use of a phrase.
"""
import csv,json,re
from pathlib import Path
from collections import Counter
ROOT=Path(__file__).resolve().parents[1]
MASTER=ROOT/"data/KEYWORD_INVENTORY.csv"
REPORT=ROOT/"data/DATE_RESEARCH_013_REPORT.json"
INDEX=ROOT/"batches/DATE_RESEARCH_013_FINAL_1600.md"
PAGES=ROOT/"batches/date-research-013"
FIX=[
 ("AIH-18510","sequence diagram","1997","early_standard_documentation",
  "Unified Modeling Language Specification Version 1.1",
  "https://www.omg.org/spec/UML/1.1/About-UML",
  "Object Management Group",
  "OMG adopted UML 1.1 in December 1997, documenting UML sequence diagrams. This replaces an unrelated 1966 source; other non-UML sequence-diagram terminology may predate UML."),
 ("AIH-18511","sequence diagrams","1997","early_standard_documentation",
  "Unified Modeling Language Specification Version 1.1",
  "https://www.omg.org/spec/UML/1.1/About-UML",
  "Object Management Group",
  "OMG UML 1.1 was adopted December 1997 and formally describes sequence diagrams. Replaces an unrelated human-factors 1961 title; NOT first-ever use of phrase."),
 ("AIH-18522","software product quality","1982","early_software_quality_publication",
  "Software Product Quality Assurance",
  "https://doi.org/10.1109/AFIPS.1982.74",
  "John R. Ryan",
  "AFIPS National Computer Conference paper (1982), pages 393–398; DOI itself contains 1982. The earlier imported 1899 year is a bibliographic metadata error. This is early technical evidence, not proven first use."),
 ("AIH-20004","network codes","2000","foundational_network_coding_publication",
  "Network Information Flow",
  "https://doi.org/10.1109/18.850663",
  "Rudolf Ahlswede; Ning Cai; Shuo-Yen Robert Li; Raymond W. Yeung",
  "July 2000 foundational network coding method paper, describing coding at network nodes. This is the method's introduction era; the plural phrase network codes may have earlier meanings."),
 ("AIH-20100","perfect secrecy","1949","original_published_secrecy_theory",
  "Communication Theory of Secrecy Systems",
  "https://doi.org/10.1002/j.1538-7305.1949.tb00928.x",
  "Claude E. Shannon",
  "Shannon's October 1949 published perfect-secrecy theory; paper notes a confidential predecessor dated September 1, 1945. This is a foundational publication rather than proof of first expression use."),
]
REJECT=[
 ("AIH-19508","co-operative systems","https://doi.org/10.1038/151523a0",
  "1943 generic co-operative systems paper lacks a specific AI-infrastructure or computing connection."),
 ("AIH-19017","power outage","https://doi.org/10.2172/4813372",
  "1961 power-utility report does not establish the origin of a Speech & Audio technology term."),
]
def main():
    with MASTER.open(newline="",encoding="utf-8-sig") as f:
        dr=csv.DictReader(f);fields=list(dr.fieldnames or []);rows=list(dr)
    assert len(rows)==20100 and len({r["id"] for r in rows})==20100
    byid={r["id"]:r for r in rows}
    audited=[]
    for uid,word,year,kind,title,url,authors,reason in FIX:
        r=byid[uid]
        assert r["keyword"]==word and not r.get("first_use_date")
        old={"year":r.get("historical_evidence_date"),"source":r.get("historical_evidence_url")}
        r.update(historical_evidence_date=year,historical_evidence_type=kind,
                 historical_evidence_title=title,historical_evidence_url=url,
                 historical_evidence_authors=authors,historical_evidence_notes=reason,
                 date_status="documented_source_not_first_use",display_date=year)
        for k in ("estimated_first_use_year","estimated_source_url","estimated_source_title","estimated_reason","estimated_confidence"):
            r[k]=""
        audited.append({"id":uid,"term":word,"old":old,"new_year":year,"source":url,"explanation":reason})
    for uid,word,url,reason in REJECT:
        r=byid[uid]
        assert r["keyword"]==word and not r.get("first_use_date")
        assert r.get("historical_evidence_url","").lower()==url.lower(),(uid,r.get("historical_evidence_url"))
        old_year=r.get("historical_evidence_date","")
        for k in ("historical_evidence_date","historical_evidence_title","historical_evidence_url","historical_evidence_authors"):
            r[k]=""
        r["historical_evidence_type"]="withdrawn_cross_domain"
        r["historical_evidence_notes"]="Rejected unrelated "+url+": "+reason
        r["date_status"]="unresolved"
        r["display_date"]=""
        audited.append({"id":uid,"term":word,"old_year":old_year,"source_removed":url,"explanation":reason})
    with MASTER.open("w",newline="",encoding="utf-8") as f:
        writer=csv.DictWriter(f,fieldnames=fields,lineterminator="\n")
        writer.writeheader();writer.writerows(rows)
    group=[r for r in rows if 18501<=int(r["id"].split("-")[-1])<=20100]
    tally=Counter(r.get("date_status") for r in group)
    assert len(group)==1600 and sum(tally.values())==1600
    assert set(tally).issubset({"documented_source_not_first_use","estimated_star","unresolved"})
    correction_ids={x[0] for x in FIX}|{x[0] for x in REJECT}
    visited=set()
    for page_num,target_count in ((1,500),(2,500),(3,500),(4,100)):
        file=PAGES/f"page-{page_num:02d}.md"
        lines=file.read_text(encoding="utf-8").splitlines()
        for i,line in enumerate(lines):
            if not line.startswith("| AIH-"):continue
            uid=line.split("|")[1].strip()
            if uid not in correction_ids:continue
            visited.add(uid)
            r=byid[uid]
            if r["date_status"]=="unresolved":
                date="—";status="Cross-domain source withdrawn";source="—"
            else:
                date=r["historical_evidence_date"]
                status="Original/early technical source (first-use unverified)"
                source="[Source]("+r["historical_evidence_url"]+")"
            lines[i]="| "+" | ".join((uid,r["keyword"],r["field"],date,status,source))+" |"
        file.write_text("\n".join(lines)+"\n",encoding="utf-8")
        assert sum(l.startswith("| AIH-") for l in lines)==target_count
    assert visited==correction_ids
    rep=json.loads(REPORT.read_text(encoding="utf-8"))
    rep.update(
        documented_source_dates=tally["documented_source_not_first_use"],
        estimated_star_dates=tally["estimated_star"],
        unresolved=tally["unresolved"],
        dated_or_estimated=tally["documented_source_not_first_use"]+tally["estimated_star"],
        manually_corrected_early_sources=len(FIX),
        withdrawn_unrelated_sources=len(REJECT),
        audited_source_corrections=audited)
    REPORT.write_text(json.dumps(rep,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    index=INDEX.read_text(encoding="utf-8")
    for label,n in (("Linked publication dates",tally["documented_source_not_first_use"]),
                    ("Estimated years ★",tally["estimated_star"]),("Unresolved",tally["unresolved"])):
        index=re.sub(r"(\| "+re.escape(label)+r" \| )\d+( \|)",lambda m:m.group(1)+str(n)+m.group(2),index)
    if "## Semantic source audit" not in index:
        index+="\n## Semantic source audit\n\nFive earlier technical sources corrected, and two unrelated source matches withdrawn. These are dated milestones, not proven coinages of exact words.\n\n"
        for item in audited:
            if "new_year" in item:
                index+=f"- **{item['id']} {item['term']}**: {item['new_year']} ([early source]({item['source']})). {item['explanation']}\n"
            else:
                index+=f"- **{item['id']} {item['term']}**: unrelated dated source withdrawn. {item['explanation']}\n"
    INDEX.write_text(index,encoding="utf-8")
    print(json.dumps({"documented_source_dates":tally["documented_source_not_first_use"],"estimated_star_dates":tally["estimated_star"],
                      "unresolved":tally["unresolved"],"manual_corrections":len(FIX),"withdrawn":len(REJECT)}))
if __name__=="__main__":main()
