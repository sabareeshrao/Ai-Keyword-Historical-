#!/usr/bin/env python3
"""Correct historically misleading Batch 007 matches using primary research.
Dates are documentary sources/method-introductions, not proven first-ever terms.
"""
import csv,json,re
from pathlib import Path
from collections import Counter

ROOT=Path(__file__).resolve().parents[1]
DB=ROOT/"data/KEYWORD_INVENTORY.csv"
BATCH=ROOT/"batches/DATE_RESEARCH_007_NEXT_2000.md"
REPORT=ROOT/"data/DATE_RESEARCH_007_REPORT.json"
PAGES=ROOT/"batches/date-research-007"

CORRECTIONS=[
("AIH-06506","Mistral","2023","original_ai_model_release",
 "Mistral 7B","https://mistral.ai/news/announcing-mistral-7b/",
 "Mistral AI team","Official 27 September 2023 release of the Mistral 7B language model. 'Mistral' as a general word existed much earlier; this date applies only to the AI model/brand."),
("AIH-06507","Morphology","1983","early_computational_nlp_attestation",
 "Two-Level Model for Morphological Analysis","https://ijcai.org/proceedings/1983/164",
 "Kimmo Koskenniemi","Earliest cited computational morphology/NLP research lead, presented at IJCAI 1983. Does NOT establish the historical first use of 'morphology', a much older term. Replaces unrelated 1935 entomology hit."),
("AIH-06513","Stochastic Variational Inference (SVI)","2013","primary_method_publication",
 "Stochastic Variational Inference","https://jmlr.org/papers/v14/hoffman13a.html",
 "Matthew D. Hoffman; David M. Blei; Chong Wang; John Paisley","Original JMLR 2013 paper introducing stochastic variational inference. Replaces an unsupported 2026 starred estimate."),
("AIH-06523","Mixture of Agents (MoA)","2024","primary_method_publication",
 "Mixture-of-Agents Enhances Large Language Model Capabilities","https://arxiv.org/abs/2406.04692",
 "Junlin Wang; Jue Wang; Ben Athiwaratkun; Ce Zhang; James Zou","Original June 2024 MoA language-model method paper. Replaces an incorrectly late 2026 starred estimate."),
("AIH-07007","Raft","2014","primary_consensus_method_publication",
 "In Search of an Understandable Consensus Algorithm","https://www.usenix.org/conference/atc14/technical-sessions/presentation/ongaro",
 "Diego Ongaro; John Ousterhout","USENIX ATC 2014 original Raft distributed consensus algorithm; this is not a claim about unrelated senses of the word raft."),
("AIH-07501","Leaky ReLU","2013","early_ai_method_attestation",
 "Rectifier Nonlinearities Improve Neural Network Acoustic Models","https://ai.stanford.edu/~amaas/papers/relu_hybrid_icml2013_final.pdf",
 "Andrew L. Maas; Awni Y. Hannun; Andrew Y. Ng","2013 primary neural-network paper investigating leaky rectified-linear activation units; earlier than 2016 retrieved mention. Exact first phrasing not conclusively established."),
("AIH-07505","RANSAC","1981","primary_method_publication",
 "Random Sample Consensus: A Paradigm for Model Fitting with Applications to Image Analysis and Automated Cartography","https://doi.org/10.1145/358669.358692",
 "Martin A. Fischler; Robert C. Bolles","Original Communications of the ACM 1981 method introducing RANSAC. Search returned no title match because full acronym not in publication title."),
("AIH-08004","Movement Pruning","2020","primary_method_publication",
 "Movement Pruning: Adaptive Sparsity by Fine-Tuning","https://arxiv.org/abs/2005.07683",
 "Victor Sanh; Thomas Wolf; Alexander M. Rush","Original May 2020 research preprint introducing Movement Pruning; replaces later 2022 reference."),
("AIH-08009","Fourier Neural Operator (FNO)","2020","primary_method_publication",
 "Fourier Neural Operator for Parametric Partial Differential Equations","https://arxiv.org/abs/2010.08895",
 "Zongyi Li; Nikola Kovachki; Kamyar Azizzadenesheli; Burigede Liu; Kaushik Bhattacharya; Andrew Stuart; Anima Anandkumar","Original October 2020 FNO preprint, later ICLR 2021; replaces later 2025 application paper."),
]

def main():
    with DB.open(encoding="utf-8-sig",newline="") as f:
        rd=csv.DictReader(f);columns=list(rd.fieldnames or []);rows=list(rd)
    assert len(rows)==20100
    lookup={r["id"]:r for r in rows}
    assert len(lookup)==20100
    old_states=[]
    for uid,word,year,typ,title,url,authors,reason in CORRECTIONS:
        r=lookup[uid]
        assert r["keyword"]==word and 6501<=int(uid[-5:])<=8500
        assert not r.get("first_use_date"),"Do not overwrite verified term origin"
        old_states.append({"id":uid,"keyword":word,"old_source_year":r.get("historical_evidence_date") or "",
                           "old_estimated_year":r.get("estimated_first_use_year") or "",
                           "new_evidence_year":year,"new_source":url,"reason":reason})
        r["historical_evidence_date"]=year
        r["historical_evidence_type"]=typ
        r["historical_evidence_title"]=title
        r["historical_evidence_url"]=url
        r["historical_evidence_authors"]=authors
        r["historical_evidence_notes"]=reason
        r["estimated_first_use_year"]=""
        r["estimated_source_url"]=""
        r["estimated_source_title"]=""
        r["estimated_reason"]=""
        r["estimated_confidence"]=""
        r["date_status"]="documented_source_not_first_use"
        r["display_date"]=year
    with DB.open("w",encoding="utf-8",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=columns,lineterminator="\n")
        writer.writeheader();writer.writerows(rows)
    for page_i in range(1,5):
        path=PAGES/f"page-{page_i:02d}.md"
        lines=path.read_text(encoding="utf-8").splitlines()
        for i,line in enumerate(lines):
            if not line.startswith("| AIH-"):continue
            uid=line.split("|")[1].strip()
            if uid not in {x[0] for x in CORRECTIONS}:continue
            r=lookup[uid]
            label=("Early NLP publication" if uid=="AIH-06507" else
                   "Early AI method paper" if uid=="AIH-07501" else
                   "Original source/publication")
            lines[i]="| "+" | ".join([uid,r["keyword"],r["field"],r["display_date"],
                                     label,"[Source]("+r["historical_evidence_url"]+")"])+" |"
        path.write_text("\n".join(lines)+"\n",encoding="utf-8")
        assert sum(line.startswith("| AIH-") for line in lines)==500
    selected=[r for r in rows if 6501<=int(r["id"].split("-")[-1])<=8500]
    tally=Counter(r["date_status"] for r in selected)
    count_doc=tally["documented_source_not_first_use"]
    count_est=tally["estimated_star"]
    count_no=tally["unresolved"]
    assert count_doc+count_est+count_no==2000
    report=json.loads(REPORT.read_text(encoding="utf-8"))
    report.update(documented_source_dates=count_doc,estimated_star_dates=count_est,
                  unresolved=count_no,dated_or_estimated=count_doc+count_est,
                  manual_semantic_corrections=len(CORRECTIONS),
                  manually_verified_primary_source_corrections=old_states)
    REPORT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    index=BATCH.read_text(encoding="utf-8")
    index=re.sub(r"(\| Linked publication dates \| )\d+( \|)",rf"\g<1>{count_doc}\g<2>",index)
    index=re.sub(r"(\| Estimated years ★ \| )\d+( \|)",rf"\g<1>{count_est}\g<2>",index)
    index=re.sub(r"(\| Unresolved \| )\d+( \|)",rf"\g<1>{count_no}\g<2>",index)
    if "## Primary-source corrections" not in index:
        index+="\n## Primary-source corrections\n\n"
        index+=f"{len(CORRECTIONS)} manually researched corrections improve the original automatic source matches. All preserve IDs and source URLs. These are documented publications or early usage, not conclusive first-ever word coinage.\n\n"
        for detail in old_states:
            index+=f"- **{detail['id']} {detail['keyword']}** — **{detail['new_evidence_year']}**, [source]({detail['new_source']}). {detail['reason']}\n"
    BATCH.write_text(index,encoding="utf-8")
    print(json.dumps({"corrected":len(CORRECTIONS),"documented":count_doc,
                      "starred_estimates":count_est,"unresolved":count_no},indent=2))
if __name__=="__main__":
    main()
