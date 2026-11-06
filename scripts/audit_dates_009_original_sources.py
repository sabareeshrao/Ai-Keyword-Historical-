#!/usr/bin/env python3
"""Review the most consequential Batch 009 ML/RL terminology matches.

An earlier primary publication is a documented historical anchor, not
necessarily the earliest appearance of the precise modern phrase.
Source/domain mismatches are withdrawn rather than promoted as AI dates.
"""
import csv,json,re
from pathlib import Path
from collections import Counter

ROOT=Path(__file__).resolve().parents[1]
MASTER=ROOT/"data/KEYWORD_INVENTORY.csv"
REPORT=ROOT/"data/DATE_RESEARCH_009_REPORT.json"
INDEX=ROOT/"batches/DATE_RESEARCH_009_NEXT_2000.md"
PAGES=ROOT/"batches/date-research-009"

FIX=[
 ("AIH-11004","k nearest neighbor algorithm","1967","early_nearest_neighbor_method_paper",
  "Nearest Neighbor Pattern Classification","https://doi.org/10.1109/TIT.1967.1053964",
  "Thomas M. Cover; Peter E. Hart",
  "1967 IEEE paper analyzing nearest-neighbor classification, including k-nearest neighbors; earlier Fix–Hodges reports exist. This is not proof of the first-ever use of the exact phrase."),
 ("AIH-11005","k-means algorithm","1966","early_kmeans_report",
  "Some Methods for Classification and Analysis of Multivariate Observations",
  "https://ntrl.ntis.gov/NTRL/dashboard/searchResults/titleDetail/AD632526.xhtml",
  "James B. MacQueen",
  "1966 U.S. NTIS indexed technical report explicitly describes and names k-means; the better-known Berkeley Symposium proceedings version appeared in 1967. Neither necessarily proves earliest algorithmic concept."),
 ("AIH-11006","k-means algorithms","1966","early_kmeans_report",
  "Some Methods for Classification and Analysis of Multivariate Observations",
  "https://ntrl.ntis.gov/NTRL/dashboard/searchResults/titleDetail/AD632526.xhtml",
  "James B. MacQueen",
  "1966 NTIS technical report documents the named k-means procedure, prior to the 1967 proceedings; this is an early concept anchor and not first-ever plural phrasing."),
 ("AIH-11007","k-means clustering","1966","early_kmeans_report",
  "Some Methods for Classification and Analysis of Multivariate Observations",
  "https://ntrl.ntis.gov/NTRL/dashboard/searchResults/titleDetail/AD632526.xhtml",
  "James B. MacQueen",
  "1966 technical report describes k-means clustering. Its published 1967 proceedings version confirms the method, but the exact modern phrase 'k-means clustering' may postdate the original report."),
 ("AIH-11009","k-nearest neighbor","1967","early_nearest_neighbor_method_paper",
  "Nearest Neighbor Pattern Classification","https://doi.org/10.1109/TIT.1967.1053964",
  "Thomas M. Cover; Peter E. Hart",
  "1967 foundational IEEE paper documenting k-nearest-neighbor decision rules. Fix and Hodges reported nonparametric nearest-neighbor classification earlier, in 1951; true first phrase use not independently established."),
 ("AIH-11011","k-nn algorithm","1967","early_nearest_neighbor_method_paper",
  "Nearest Neighbor Pattern Classification","https://doi.org/10.1109/TIT.1967.1053964",
  "Thomas M. Cover; Peter E. Hart",
  "1967 paper analyzing nearest-neighbor rules; the abbreviation K-NN and exact modern term may have appeared later. The dated source documents the method rather than confirmed first abbreviation use."),
 ("AIH-11504","temporal differences","1988","primary_temporal_difference_learning_paper",
  "Learning to Predict by the Methods of Temporal Differences",
  "https://doi.org/10.1007/BF00115009",
  "Richard S. Sutton",
  "1988 Machine Learning journal paper providing foundational temporal-difference learning methods. An unrelated 1981 acoustics title previously matched the generic words."),
]
REJECT=[
 ("AIH-10517","perceived risk",
  "https://doi.org/10.1177/002224376400100405",
  "1964 Journal of Marketing paper concerns consumer perception of risk; it does not document a concept introduced in AI infrastructure."),
 ("AIH-11019","microbispora",
  "https://doi.org/10.1099/00207713-15-3-139",
  "1965 microbiology publication concerns a bacterial genus. The inventory category Machine Learning appears misclassified, so this must not be presented as an AI research term-origin date."),
]

def main():
    with MASTER.open(encoding="utf-8-sig",newline="") as f:
        rd=csv.DictReader(f)
        columns=list(rd.fieldnames)
        rows=list(rd)
    assert len(rows)==20100 and len({r["id"] for r in rows})==20100
    by_id={r["id"]:r for r in rows}
    details=[]
    corrections={}
    for uid,term,year,typ,title,url,authors,explanation in FIX:
        r=by_id[uid]
        assert r["keyword"]==term and 10501<=int(uid[-5:])<=12500
        assert not r.get("first_use_date")
        prev={"date":r.get("historical_evidence_date"),"estimate":r.get("estimated_first_use_year"),"source":r.get("historical_evidence_url") or r.get("estimated_source_url")}
        r["historical_evidence_date"]=year
        r["historical_evidence_type"]=typ
        r["historical_evidence_title"]=title
        r["historical_evidence_url"]=url
        r["historical_evidence_authors"]=authors
        r["historical_evidence_notes"]=explanation
        for k in ("estimated_first_use_year","estimated_source_url","estimated_source_title","estimated_reason","estimated_confidence"):
            r[k]=""
        r["date_status"]="documented_source_not_first_use"
        r["display_date"]=year
        details.append({"id":uid,"keyword":term,"old":prev,"new_year":year,"new_source":url,"reason":explanation})
        corrections[uid]=r
    for uid,term,old_url,reason in REJECT:
        r=by_id[uid]
        assert r["keyword"]==term and not r.get("first_use_date")
        assert (r.get("historical_evidence_url") or "").lower()==old_url.lower(),r.get("historical_evidence_url")
        old_date=r["historical_evidence_date"]
        for k in ("historical_evidence_date","historical_evidence_title","historical_evidence_url","historical_evidence_authors"):
            r[k]=""
        r["historical_evidence_type"]="cross_domain_source_withdrawn"
        r["historical_evidence_notes"]="Previously cited "+old_date+" "+old_url+" removed: "+reason
        r["display_date"]=""
        r["date_status"]="unresolved"
        details.append({"id":uid,"keyword":term,"old_year":old_date,"removed_source":old_url,"reason":reason})
        corrections[uid]=r
    group=[r for r in rows if 10501<=int(r["id"].split("-")[-1])<=12500]
    counts=Counter(r.get("date_status") for r in group)
    assert len(group)==2000
    assert sum(counts.values())==2000
    assert set(counts).issubset({"documented_source_not_first_use","estimated_star","unresolved"})
    with MASTER.open("w",encoding="utf-8",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=columns,lineterminator="\n")
        writer.writeheader();writer.writerows(rows)
    found=set()
    for i in range(1,5):
        path=PAGES/f"page-{i:02d}.md"
        lines=path.read_text(encoding="utf-8").splitlines()
        for pos,line in enumerate(lines):
            if not line.startswith("| AIH-"):continue
            uid=line.split("|")[1].strip()
            row=corrections.get(uid)
            if row is None:continue
            found.add(uid)
            if row["date_status"]=="unresolved":
                date="—";tag="Unrelated source rejected";source="—"
            else:
                date=row["historical_evidence_date"];tag="Early primary research (origin unverified)"
                source="[Source]("+row["historical_evidence_url"]+")"
            lines[pos]="| "+" | ".join([uid,row["keyword"],row["field"],date,tag,source])+" |"
        path.write_text("\n".join(lines)+"\n",encoding="utf-8")
        assert sum(line.startswith("| AIH-") for line in lines)==500
    assert found==set(corrections)
    report=json.loads(REPORT.read_text(encoding="utf-8"))
    report.update(documented_source_dates=counts["documented_source_not_first_use"],
                  estimated_star_dates=counts["estimated_star"],
                  unresolved=counts["unresolved"],
                  dated_or_estimated=counts["documented_source_not_first_use"]+counts["estimated_star"],
                  manual_primary_source_corrections=len(FIX),
                  withdrawn_cross_domain_sources=len(REJECT),
                  semantic_source_audit=details)
    REPORT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    index=INDEX.read_text(encoding="utf-8")
    index=re.sub(r"(\| Linked publication dates \| )\d+( \|)",rf"\g<1>{counts['documented_source_not_first_use']}\g<2>",index)
    index=re.sub(r"(\| Estimated years ★ \| )\d+( \|)",rf"\g<1>{counts['estimated_star']}\g<2>",index)
    index=re.sub(r"(\| Unresolved \| )\d+( \|)",rf"\g<1>{counts['unresolved']}\g<2>",index)
    if "## Scholarly source QA" not in index:
        index+="\n## Scholarly source QA\n\n"
        index+="Seven method terms were corrected using early primary scholarly reports; two obviously unrelated domain sources were withdrawn. These are historical anchors, not proof of first-ever wording.\n\n"
        for d in details:
            if "new_source" in d:
                index+=f"- **{d['id']} {d['keyword']}** — {d['new_year']}, [original/early paper]({d['new_source']}). {d['reason']}\n"
            else:
                index+=f"- **{d['id']} {d['keyword']}** — withdrawn unrelated source. {d['reason']}\n"
    INDEX.write_text(index,encoding="utf-8")
    print(json.dumps({"revised_source_dates":counts["documented_source_not_first_use"],
                      "estimated_years_star":counts["estimated_star"],
                      "unresolved":counts["unresolved"],"manual_corrections":len(FIX),
                      "withdrawn_wrong_domain":len(REJECT)},indent=2))
if __name__=="__main__":main()
