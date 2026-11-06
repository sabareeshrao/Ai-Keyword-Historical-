#!/usr/bin/env python3
"""Semantic QA for batch 008: replace misleading dates with early/original sources.

The source date is not necessarily the earliest use of the exact term.
Never overwrite existing first-use proof. Mark cross-domain matches unresolved.
"""
import csv,json,re
from pathlib import Path
from collections import Counter
ROOT=Path(__file__).resolve().parents[1]
DB=ROOT/"data/KEYWORD_INVENTORY.csv"
REPORT=ROOT/"data/DATE_RESEARCH_008_REPORT.json"
INDEX=ROOT/"batches/DATE_RESEARCH_008_NEXT_2000.md"
PAGES=ROOT/"batches/date-research-008"
FIX=[
  ("AIH-08508","Masked Autoencoder (MAE)","2021","primary_method_preprint",
   "Masked Autoencoders Are Scalable Vision Learners",
   "https://arxiv.org/abs/2111.06377",
   "Kaiming He; Xinlei Chen; Saining Xie; Yanghao Li; Piotr Dollar; Ross Girshick",
   "November 2021 first public preprint of the named scalable vision MAE architecture. This does not prove earliest use of generic masked autoencoding."),
  ("AIH-08509","Position Interpolation","2023","primary_llm_method_preprint",
   "Extending Context Window of Large Language Models via Positional Interpolation",
   "https://arxiv.org/abs/2306.15595",
   "Shouyuan Chen; Sherman Wong; Liangjian Chen; Yuandong Tian",
   "Original June 2023 paper on RoPE-based LLM Position Interpolation. Previous 1949 match was unrelated to this long-context technique."),
  ("AIH-08510","WordNet","1990","early_system_documentation",
   "Introduction to WordNet: An On-line Lexical Database",
   "https://doi.org/10.1093/ijl/3.4.235",
   "George A. Miller; Richard Beckwith; Christiane Fellbaum; Derek Gross; Katherine J. Miller",
   "1990 International Journal of Lexicography documentation of the WordNet lexical database. Earlier project work may have existed; 1990 is a documented publication, not proven coinage."),
  ("AIH-08513","Matryoshka Embedding","2022","primary_research_preprint",
   "Matryoshka Representation Learning",
   "https://arxiv.org/abs/2205.13147",
   "Aditya Kusupati; Gantavya Bhatt; Aniket Rege; Matthew Wallingford; et al.",
   "May 2022 Matryoshka Representation Learning preprint, introducing variable-dimensional Matryoshka representations. Term variant 'Matryoshka Embedding' may have appeared later."),
  ("AIH-08515","WordPiece","2012","early_method_publication",
   "Japanese and Korean Voice Search",
   "https://doi.org/10.1109/ICASSP.2012.6289079",
   "Mike Schuster; Kaisuke Nakajima",
   "2012 ICASSP paper describing word-piece-based segmentation for Japanese and Korean voice search. Early published use, not independently established first-ever terminology."),
  ("AIH-09002","TIES Merging","2023","primary_method_preprint",
   "TIES-Merging: Resolving Interference When Merging Models",
   "https://arxiv.org/abs/2306.01708",
   "Prateek Yadav; Derek Tam; Leshem Choshen; Colin Raffel; Mohit Bansal",
   "Original June 2023 research preprint introducing TIES-Merging. Replaces an indirect later bibliographic hit."),
  ("AIH-09015","KL Divergence","1951","original_underlying_concept_publication",
   "On Information and Sufficiency",
   "https://doi.org/10.1214/aoms/1177729694",
   "Solomon Kullback; Richard A. Leibler",
   "Original 1951 Kullback-Leibler information divergence paper; does NOT establish first use of the precise later expression 'KL divergence'."),
  ("AIH-09502","Optical Flow","1980","early_original_technical_report",
   "Determining Optical Flow",
   "https://dspace.mit.edu/entities/publication/e7968bf6-651d-4fd0-b4e8-c608756f2bba",
   "Berthold K. P. Horn; Brian G. Schunck",
   "April 1980 MIT Artificial Intelligence Laboratory technical report AIM-572; predates 1981 journal publication. Optical flow as a broader concept predates this particular method."),
  ("AIH-10008","Top-p","2019","primary_nucleus_sampling_preprint",
   "The Curious Case of Neural Text Degeneration",
   "https://arxiv.org/abs/1904.09751",
   "Ari Holtzman; Jan Buys; Li Du; Maxwell Forbes; Yejin Choi",
   "Original April 2019 nucleus sampling paper; modern top-p text decoding derives from this method. Date is not proven first use of literal string 'Top-p'."),
]
REJECT=[
  ("AIH-08516","Feedback Loop","https://doi.org/10.1104/pp.62.3.406",
   "1978 paper on plant stomata and carbon-dioxide feedback, not a source for AI feedback loops."),
  ("AIH-10002","Tool Use","https://doi.org/10.7560/775909",
   "1987 archaeology book on prehistoric stone-tool use, not AI agent tool use."),
]

def main():
    with DB.open(encoding="utf-8-sig",newline="") as f:
        r=csv.DictReader(f);cols=list(r.fieldnames);rows=list(r)
    assert len(rows)==20100
    lookup={r["id"]:r for r in rows}
    assert len(lookup)==20100
    audit=[]
    for uid,term,year,status,title,url,authors,note in FIX:
        r=lookup[uid]
        assert r["keyword"]==term and not r.get("first_use_date")
        assert 8501<=int(uid[-5:])<=10500
        old={"date":r.get("historical_evidence_date"),"estimate":r.get("estimated_first_use_year"),
             "url":r.get("historical_evidence_url") or r.get("estimated_source_url")}
        r["historical_evidence_date"]=year
        r["historical_evidence_type"]=status
        r["historical_evidence_title"]=title
        r["historical_evidence_url"]=url
        r["historical_evidence_authors"]=authors
        r["historical_evidence_notes"]=note
        for key in ("estimated_first_use_year","estimated_source_title","estimated_source_url","estimated_reason","estimated_confidence"):r[key]=""
        r["date_status"]="documented_source_not_first_use"
        r["display_date"]=year
        audit.append({"id":uid,"term":term,"previous":old,"new_year":year,"new_source":url,"reason":note})
    for uid,term,disputed_url,reason in REJECT:
        r=lookup[uid]
        assert r["keyword"]==term and not r.get("first_use_date")
        assert r["historical_evidence_url"].lower()==disputed_url.lower(),(uid,r["historical_evidence_url"])
        prior_date=r.get("historical_evidence_date")
        r["historical_evidence_date"]=""
        r["historical_evidence_type"]="cross_domain_mismatch_removed"
        r["historical_evidence_title"]=""
        r["historical_evidence_url"]=""
        r["historical_evidence_authors"]=""
        r["historical_evidence_notes"]="Removed source "+disputed_url+" previously dated "+str(prior_date)+": "+reason+" No suitable AI-context source identified in this check."
        r["date_status"]="unresolved"
        r["display_date"]=""
        audit.append({"id":uid,"term":term,"rejected_source":disputed_url,"old_year":prior_date,"reason":reason})
    # Keep historical context and precise types, not blind dates.
    group=[r for r in rows if 8501<=int(r["id"].split("-")[-1])<=10500]
    tally=Counter(r.get("date_status") for r in group)
    assert len(group)==2000
    assert tally["documented_source_not_first_use"]+tally["estimated_star"]+tally["unresolved"]==2000
    with DB.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=cols,lineterminator="\n")
        w.writeheader();w.writerows(rows)
    modified_ids={r[0] for r in FIX}|{r[0] for r in REJECT}
    for n in range(1,5):
        path=PAGES/f"page-{n:02d}.md"
        lines=path.read_text(encoding="utf-8").splitlines()
        seen=set()
        for i,line in enumerate(lines):
            if not line.startswith("| AIH-"):continue
            uid=line.split("|")[1].strip()
            if uid not in modified_ids:continue
            row=lookup[uid]
            if row["date_status"]=="unresolved":
                year="—";kind="Cross-domain source rejected; unresolved";link="—"
            else:
                year=row["display_date"]
                kind="Original/early source (not proven first use)"
                link="[Source]("+row["historical_evidence_url"]+")"
            lines[i]="| "+" | ".join([uid,row["keyword"],row["field"],year,kind,link])+" |"
            seen.add(uid)
        path.write_text("\n".join(lines)+"\n",encoding="utf-8")
        assert sum(x.startswith("| AIH-") for x in lines)==500
    report=json.loads(REPORT.read_text(encoding="utf-8"))
    report.update(
        documented_source_dates=tally["documented_source_not_first_use"],
        estimated_star_dates=tally["estimated_star"],
        unresolved=tally["unresolved"],
        dated_or_estimated=tally["documented_source_not_first_use"]+tally["estimated_star"],
        manual_source_corrections=len(FIX),
        cross_domain_sources_rejected=len(REJECT),
        manual_correction_audit=audit)
    REPORT.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    index=INDEX.read_text(encoding="utf-8")
    index=re.sub(r"(\| Linked publication dates \| )\d+( \|)",rf"\g<1>{tally['documented_source_not_first_use']}\g<2>",index)
    index=re.sub(r"(\| Estimated years ★ \| )\d+( \|)",rf"\g<1>{tally['estimated_star']}\g<2>",index)
    index=re.sub(r"(\| Unresolved \| )\d+( \|)",rf"\g<1>{tally['unresolved']}\g<2>",index)
    if "## Human research source audit" not in index:
        index+="\n## Human research source audit\n\n"
        index+="Nine historically important terms were corrected to original or early scholarly sources; two unrelated cross-domain citations were rejected. All original IDs remain unchanged.\n\n"
        for item in audit:
            if "new_source" in item:
                index+=f"- {item['id']} **{item['term']}**: {item['new_year']} ([research source]({item['new_source']})). {item['reason']}\n"
            else:
                index+=f"- {item['id']} **{item['term']}**: old date withdrawn. {item['reason']}\n"
    INDEX.write_text(index,encoding="utf-8")
    print(json.dumps({"manual_corrections":len(FIX),"cross_domain_rejections":len(REJECT),
                      "documented_dates":tally["documented_source_not_first_use"],
                      "star_estimates":tally["estimated_star"],"unresolved":tally["unresolved"]},indent=2))
if __name__=="__main__":main()
