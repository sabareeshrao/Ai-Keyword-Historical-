#!/usr/bin/env python3
"""Conservatively apply six manually checked recovery sources to current main.

Reads latest master inventory at runtime. Does not revert concurrently added
Batch 005/006 columns or dates. Refuses changed/conflicting researched rows.
"""
import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "data/KEYWORD_INVENTORY.csv"
REPORT = ROOT / "data/DATE_RESEARCH_004_REPORT.json"
INDEX = ROOT / "batches/DATE_RESEARCH_004_RECOVERY_FIRST_1000.md"
README = ROOT / "README.md"
PAGES = [ROOT / "batches/date-research-004/page-01.md",
         ROOT / "batches/date-research-004/page-02.md"]

# id, year, classification, author, original publication, reference, reasoning, confidence
FINDINGS = [
 ("AIH-00836","1962","estimated","Jacques F. Benders",
  "Partitioning procedures for solving mixed-variables programming problems",
  "https://doi.org/10.1007/BF01386316",
  "ESTIMATE: 1962 original publication of the decomposition method; the later name 'Benders decomposition' is not proven to have appeared in the original paper. Method invention is not the exact expression's coinage.","Medium"),
 ("AIH-01001","2018","earliest_known","Keyulu Xu; Weihua Hu; Jure Leskovec; Stefanie Jegelka",
  "How Powerful are Graph Neural Networks?",
  "https://arxiv.org/abs/1810.00826",
  "October 2018 original preprint explicitly uses 'expressive power of GNNs' in its abstract. Establishes a dated term attestation, not globally first-ever use.","High"),
 ("AIH-01926","2019","earliest_known","Shibo Wang; Pankaj Kanwar; Google Cloud",
  "BFloat16: The secret to high performance on Cloud TPUs",
  "https://cloud.google.com/blog/products/ai-machine-learning/bfloat16-the-secret-to-high-performance-on-cloud-tpus",
  "Google's dated 23 August 2019 technical article explicitly names bfloat16. Refers to earlier 2018 TPU material, so this is a source attestation, not proof of original coinage.","Medium"),
 ("AIH-02230","1952","estimated","Ralph A. Bradley; Milton E. Terry",
  "Rank Analysis of Incomplete Block Designs. I. The Method of Paired Comparisons",
  "https://doi.org/10.1093/biomet/39.3-4.324",
  "ESTIMATE anchored to Bradley and Terry's 1952 model paper. The original method and its later eponym 'Bradley-Terry model' must not be conflated.","Medium"),
 ("AIH-02241","1976","estimated","Eugene Lawler (1976), as documented by historian David Walden",
  "The Bellman-Ford Algorithm and Distributed Bellman-Ford (historical investigation)",
  "https://www.walden-family.com/public/bf-history.pdf",
  "ESTIMATE: Walden reports that Lawler used 'Bellman-Ford method' in 1976; the algorithms were independently published by Ford in 1956 and Bellman in 1958. Original first use of 'Bellman-Ford Algorithm' is unproven.","Medium"),
 ("AIH-02253","2022","earliest_known","Yuhang Lai; Chengxi Li; Yiming Wang; Tianyi Zhang; et al.",
  "DS-1000: A Natural and Reliable Benchmark for Data Science Code Generation",
  "https://arxiv.org/abs/2211.11501",
  "Original arXiv submission on 18 November 2022 explicitly introduced the DS-1000 benchmark, preceding its 2023 ICML proceedings publication.","High"),
]
MAP = {x[0]:x for x in FINDINGS}

def safe(s):
    return str(s or "").replace("|", "/").replace("\n", " ").strip()

def main():
    with MASTER.open(encoding="utf-8-sig", newline="") as fp:
        reader=csv.DictReader(fp); headers=reader.fieldnames; rows=list(reader)
    assert len(rows)==20100 and len({r["id"] for r in rows})==20100
    necessary={"historical_date","date_status","display_date","is_estimated","original_researcher",
               "original_publication","source_url","explanation","confidence","recovery_batch"}
    assert necessary.issubset(set(headers))
    mapping={r["id"]:r for r in rows}
    updated=0
    for id,year,status,author,paper,url,reason,confidence in FINDINGS:
        row=mapping[id]
        if row.get("historical_date"):
            if row["historical_date"]==year and row["date_status"]==status:
                continue
            raise RuntimeError("Refusing to overwrite a newly researched date for "+id)
        if row["recovery_batch"]!="004_pending_recheck":
            raise RuntimeError("Refusing to replace externally modified record "+id)
        if row.get("estimated_first_use_year"):
            raise RuntimeError("Other research added an estimate for "+id)
        row.update(historical_date=year,date_status=status,
                   display_date=year+(" ★" if status=="estimated" else ""),
                   is_estimated="true" if status=="estimated" else "false",
                   original_researcher=author,original_publication=paper,
                   source_url=url,explanation=reason,confidence=confidence,
                   recovery_batch="004_researched")
        updated+=1
    assert sum(bool(r["historical_date"]) for r in rows if r.get("recovery_batch")=="004_researched")==31
    assert sum(r.get("recovery_batch")=="004_pending_recheck" for r in rows)==969
    for page in PAGES:
        original=page.read_text(encoding="utf-8")
        newlines=[]
        for line in original.splitlines():
            if not line.startswith("| AIH-"):
                newlines.append(line);continue
            fields=[x.strip() for x in line.strip("|").split("|")]
            if fields[0] not in MAP:
                newlines.append(line);continue
            assert len(fields)==10,fields
            id,year,status,author,paper,url,reason,confidence=MAP[fields[0]]
            fields[3]=year+(" ★" if status=="estimated" else "")
            fields[4]=status
            fields[5]=author
            fields[6]=paper
            fields[7]="[Original source]("+url+")"
            fields[8]=confidence
            fields[9]=reason
            newlines.append("| "+" | ".join(map(safe,fields))+" |")
        assert sum(bool(re.match(r"^\| AIH-\d{5} \|",s)) for s in newlines)==500
        page.write_text("\n".join(newlines)+"\n",encoding="utf-8")
    documented=sum(r["recovery_batch"]=="004_researched" and
                    r["date_status"]!="estimated" for r in rows)
    estimated=sum(r["recovery_batch"]=="004_researched" and
                  r["date_status"]=="estimated" for r in rows)
    assert (documented,estimated)==(26,5)
    all_dated=sum(bool(r.get("first_use_date") or r.get("historical_evidence_date")
                      or r.get("historical_date") or r.get("estimated_first_use_year"))
                  for r in rows)
    with MASTER.open("w",encoding="utf-8",newline="") as fp:
        writer=csv.DictWriter(fp,fieldnames=headers,lineterminator="\n")
        writer.writeheader();writer.writerows(rows)
    report=json.loads(REPORT.read_text(encoding="utf-8"))
    report.update(
        documented_method_or_exact_phrase_attestations=documented,estimated_dates=estimated,
        newly_dated_count=31,still_unresolved_in_selection=969,
        newly_rechecked_date_items=31,pending_recheck=969,
        total_dates_in_repository_including_preserved_attestations=all_dated,
        recovery_004_dates_including_original_1350=1350+31,
        undated_inventory_after_update=20100-all_dated,
        caution="The 1000-row recovery selection includes 969 entries still requiring independent primary-source research. No completed 1000-term claim is made."
    )
    REPORT.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    txt=INDEX.read_text(encoding="utf-8")
    replacements={
      "25 received new evidence review; **975 remain pending":"31 received new evidence review; **969 remain pending",
      "| Newly reviewed and date populated | 25 |":"| Newly reviewed and date populated | 31 |",
      "| Qualified earliest-known research/term attestations | 23 |":"| Qualified earliest-known research/term attestations | 26 |",
      "| Estimated approximate dates marked ★ | 2 |":"| Estimated approximate dates marked ★ | 5 |",
      "| Still unresolved / pending fresh review | 975 |":"| Still unresolved / pending fresh review | 969 |",
      "| Total populated dates counting new and preserved attestations | 1,375 |":"| Recovery 004 plus original 1,350 dates | 1,381 |",
      "Exactly 975 selected entries still need":"Exactly 969 selected entries still need",
    }
    for before,after in replacements.items():
        txt=txt.replace(before,after)
    txt=txt.replace("## Auditable results",f"**Repository-wide distinct dated records (all research series): {all_dated:,}.**\n\n## Auditable results")
    INDEX.write_text(txt,encoding="utf-8")
    readme=README.read_text(encoding="utf-8")
    readme=readme.replace(
        "25 independently reviewed dated leads (23 references + 2 ★ estimates), 975 pending",
        "31 independently reviewed dated leads (26 references + 5 ★ estimates), 969 pending"
    ).replace(
        "25 reviews and status of remaining unresolved terms",
        "31 reviews and status of remaining unresolved terms"
    )
    readme=readme.replace("## Date research progress",
        "**[Recovery methodology](docs/HISTORICAL_DATE_RECOVERY_PROTOCOL.md)** · "
        "[Exact-phrase research candidate script](scripts/recovery_evidence_discovery.py). "
        "Source candidates require original-publication verification before being treated as historical dates.\n\n## Date research progress")
    README.write_text(readme,encoding="utf-8")
    print(json.dumps({"newly_applied":updated,"documented_recovery":documented,
                      "estimated_recovery":estimated,"still_pending":969,
                      "repository_wide_distinct_dated_records":all_dated,
                      "status":"partial_not_completed"},indent=2))
if __name__=="__main__":
    main()
