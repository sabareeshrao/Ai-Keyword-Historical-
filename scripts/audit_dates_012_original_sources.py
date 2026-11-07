#!/usr/bin/env python3
"""Batch 012 semantic audit: original/early sources and cross-domain withdrawals.

Dates in source evidence columns are dated technical records, not independently
established first-ever use of each exact expression. Preserve ★★ speculation.
"""
import csv,json,re
from pathlib import Path
from collections import Counter

ROOT=Path(__file__).resolve().parents[1]
MASTER=ROOT/"data/KEYWORD_INVENTORY.csv"
REPORT=ROOT/"data/DATE_RESEARCH_012_REPORT.json"
INDEX=ROOT/"batches/DATE_RESEARCH_012_NEXT_2000.md"
PAGES=ROOT/"batches/date-research-012"
FIX=[
("AIH-16512","optical packet switching","1991","early_photonic_packet_switch_publication",
 "Self-routing crossbar packet switch employing free-space optics for chip-to-chip interconnections",
 "https://doi.org/10.1364/AO.30.003721","Thomas J. Cloonan; Anthony L. Lentine",
 "1991 peer-reviewed photonic packet switching architecture; an original 1990 Bell Labs manuscript predates publication. Earlier unrelated 1970 source withdrawn. Not proven first exact term use."),
("AIH-17002","udp","1980","original_internet_protocol_specification",
 "User Datagram Protocol (RFC 768)","https://www.rfc-editor.org/info/rfc768/",
 "Jon Postel","RFC 768 introduced and defined UDP on 28 August 1980; first original protocol specification, not first possible acronym usage."),
("AIH-17015","unscented transformations","1997","early_unscented_filter_publication",
 "New Extension of the Kalman Filter to Nonlinear Systems",
 "https://doi.org/10.1117/12.280797","Simon J. Julier; Jeffrey K. Uhlmann",
 "1997 original unscented Kalman filter family research documenting the approach, predating the 2017 later application. A 1995 precursor also exists; exact first plural wording unverified."),
("AIH-18001","boosting algorithm","1990","foundational_boosting_method_publication",
 "The Strength of Weak Learnability",
 "https://doi.org/10.1007/BF00116037","Robert E. Schapire",
 "1990 foundational boosting method paper, before a 2008 application. Historical method anchor; not proof that the exact phrase 'boosting algorithm' first appeared in 1990."),
("AIH-18003","c4.5 algorithm","1992","early_original_c45_book",
 "C4.5: Programs for Machine Learning",
 "https://shop.elsevier.com/books/c45/quinlan/978-0-08-050058-4","J. Ross Quinlan",
 "Original publisher lists first edition 1 October 1992; some academic catalogs report 1993. The year is publisher-dated early C4.5 documentation, not verified first use of exact phrase."),
("AIH-18013","connected component analysis","1965","early_digital_picture_technical_report",
 "Pattern Recognition IV: Sequential Operations in Digital Picture Processing",
 "https://ntrs.nasa.gov/citations/19650019588","Azriel Rosenfeld; John L. Pfaltz",
 "May 1965 NASA contractor report on sequential connected-component labeling in digital images, earlier than 1966 journal article and 1996 citation; first exact phrase unverified."),
]
REJECT=[
("AIH-17505","low resolution","https://doi.org/10.1016/0022-2836(73)90214-3",
 "1973 paper is molecular biology; it does not establish the history of low-resolution imagery or computer vision."),
("AIH-17509","fusion methods","https://doi.org/10.1021/ac60028a004",
 "1949 analytical chemistry paper is not a historical anchor for image-fusion methods."),
("AIH-17510","fusion process","https://doi.org/10.1038/scientificamerican01081910-23asupp",
 "1910 Scientific American discussion is an unrelated generic fusion process, not computer vision."),
("AIH-17516","gear manufacture","https://doi.org/10.1049/jipe.1935.0064",
 "1935 manufacturing paper is outside the computer-vision sense; term requires scope review."),
("AIH-18014","conservation status","https://doi.org/10.1016/0006-3207(73)90146-8",
 "1973 conservation biology usage does not establish machine-learning terminology; category requires review."),
]
def main():
    with MASTER.open(encoding="utf-8-sig",newline="") as f:
        reader=csv.DictReader(f);columns=list(reader.fieldnames or []);rows=list(reader)
    assert len(rows)==20100 and len({r["id"] for r in rows})==20100
    byid={r["id"]:r for r in rows}
    edited={}; audit=[]
    for uid,term,year,etype,title,url,authors,note in FIX:
        r=byid[uid]
        assert r["keyword"]==term and not r.get("first_use_date")
        before={"document_year":r.get("historical_evidence_date"),"estimated_year":r.get("estimated_first_use_year"),"source":r.get("historical_evidence_url")}
        r.update(historical_evidence_date=year,historical_evidence_type=etype,
                 historical_evidence_title=title,historical_evidence_url=url,
                 historical_evidence_authors=authors,historical_evidence_notes=note,
                 date_status="documented_source_not_first_use",display_date=year)
        for key in ("estimated_first_use_year","estimated_source_url","estimated_source_title","estimated_reason","estimated_confidence"):
            r[key]=""
        edited[uid]=r
        audit.append({"id":uid,"term":term,"before":before,"source_year":year,"source_url":url,"note":note})
    for uid,term,url,note in REJECT:
        r=byid[uid]
        assert r["keyword"]==term and not r.get("first_use_date")
        assert (r.get("historical_evidence_url") or "").lower() in ("",url.lower()),(uid,r.get("historical_evidence_url"))
        before={"date":r.get("historical_evidence_date"),"source":r.get("historical_evidence_url")}
        for key in ("historical_evidence_date","historical_evidence_title","historical_evidence_url","historical_evidence_authors"):
            r[key]=""
        r["historical_evidence_type"]="cross_domain_source_withdrawn"
        r["historical_evidence_notes"]=note+" Rejected: "+url
        r["date_status"]="unresolved"
        r["display_date"]=""
        edited[uid]=r
        audit.append({"id":uid,"term":term,"before":before,"status":"withdrawn_cross_domain","reason":note})
    chosen=[r for r in rows if 16501<=int(r["id"].split("-")[-1])<=18500]
    tally=Counter(r.get("date_status") for r in chosen)
    assert len(chosen)==2000
    assert set(tally).issubset({"documented_source_not_first_use","estimated_star","unresolved"})
    assert sum(tally.values())==2000
    with MASTER.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=columns,lineterminator="\n")
        w.writeheader();w.writerows(rows)
    seen=set()
    for i in range(1,5):
        page=PAGES/f"page-{i:02d}.md"
        lines=page.read_text(encoding="utf-8").splitlines()
        for k,line in enumerate(lines):
            if not line.startswith("| AIH-"):continue
            uid=line.split("|")[1].strip()
            r=edited.get(uid)
            if not r:continue
            seen.add(uid)
            if r["date_status"]=="unresolved":
                y="—";tag="Unrelated source withdrawn";source="—"
            else:
                y=r["display_date"];tag="Original or early technical source (term origin unverified)"
                source="[Source]("+r["historical_evidence_url"]+")"
            lines[k]="| "+" | ".join((uid,r["keyword"],r["field"],y,tag,source))+" |"
        page.write_text("\n".join(lines)+"\n",encoding="utf-8")
        assert sum(x.startswith("| AIH-") for x in lines)==500
    assert seen==set(edited)
    report=json.loads(REPORT.read_text(encoding="utf-8"))
    report.update(documented_source_dates=tally["documented_source_not_first_use"],
                  estimated_star_dates=tally["estimated_star"],unresolved=tally["unresolved"],
                  dated_or_estimated=tally["documented_source_not_first_use"]+tally["estimated_star"],
                  manual_technical_source_checks=len(FIX),
                  cross_domain_sources_withdrawn=len(REJECT),
                  manual_semantic_source_audit=audit)
    REPORT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    index=INDEX.read_text(encoding="utf-8")
    for label,val in [("Linked publication dates",tally["documented_source_not_first_use"]),
                      ("Estimated years ★",tally["estimated_star"]),
                      ("Unresolved",tally["unresolved"])]:
        index=re.sub(r"(\| "+re.escape(label)+r" \| )\d+( \|)",lambda m:m.group(1)+str(val)+m.group(2),index)
    if "## Semantic publication-source audit" not in index:
        index+="\n## Semantic publication-source audit\n\n"
        index+="Six early technical publications were checked and corrected; five cross-domain references were withdrawn. These dates remain documented milestones, not established first wording.\n\n"
        for x in audit:
            if "source_url" in x:
                index+=f"- **{x['id']} {x['term']}**: {x['source_year']} [research source]({x['source_url']}). {x['note']}\n"
            else:
                index+=f"- **{x['id']} {x['term']}**: unrelated source withdrawn. {x['reason']}\n"
    INDEX.write_text(index,encoding="utf-8")
    print(json.dumps({"source_dates":tally["documented_source_not_first_use"],
                      "estimated_star":tally["estimated_star"],
                      "unresolved":tally["unresolved"],"corrected":len(FIX),"withdrawn":len(REJECT)}))
if __name__=="__main__":main()
