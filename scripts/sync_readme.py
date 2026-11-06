#!/usr/bin/env python3
"""Update README from audited CSV and import reports, avoiding stale claims."""
import csv,json
from pathlib import Path
from collections import Counter
root=Path(__file__).resolve().parents[1]
with (root/"data/KEYWORD_INVENTORY.csv").open(encoding="utf-8-sig",newline="") as f:
    rows=list(csv.DictReader(f))
if len(rows)!=20100:
    raise ValueError("Cannot publish completion status before 20100 records exist.")
assert len(set(r["id"] for r in rows))==20100
counts=Counter(r.get("inventory_batch") for r in rows)
assert [counts[str(i).zfill(3)] for i in range(1,5)]==[5000]*4
report=json.loads((root/"data/INVENTORY_IMPORT_REPORT_003_004.json").read_text(encoding="utf-8"))
assert report["added"]==10000 and report["inventory_total"]==20100
lines=[
"# AI Keyword Historical — Full, categorized source-backed inventory",
"",
"**Current inventory: 20,100 terms**, comprising 100 early records and four source-import batches of 5,000. Target is 21,000 (planning estimate, not a known census).",
"",
"> **Research status:** First-use historical dates remain unverified, and individual relevance of source-derived technical terms needs expert review. A source ontology topic is not proof that the term originated on any particular date.",
"",
"## Date research progress",
"",
"**[First 500 terms: historical evidence table](batches/DATE_RESEARCH_001_FIRST_500.md)** — 500 ID records and linked dated documents where found, with honest uncertainty labels.",
"",
"**[Date research quality report](data/DATE_RESEARCH_001_REPORT.json)** — attached date count and outstanding investigations. Publication dates are not proven original coinage dates.",
"",
"**[Next 1,000 term-date research (IDs AIH-00501 to AIH-01500)](batches/DATE_RESEARCH_002_NEXT_1000.md)** — two full 500-row tables, linked source-documented dates, and unresolved statuses.",
"",
"**[Research batch 002 JSON report](data/DATE_RESEARCH_002_REPORT.json)** — dated and unresolved totals.",
"",
"**[Date research 003: Next 1,000 terms (AIH-01501–AIH-02500)](batches/DATE_RESEARCH_003_NEXT_1000.md)** — two full 500-row tables with cited source dates. These are not proven term-origin dates.",
"",
"**[Date research 003 audit](data/DATE_RESEARCH_003_REPORT.json)** — count of retrieved dates and unresolved terms.",
"",
"**[Date research 004: 2,000 keywords (AIH-02501–AIH-04500)](batches/DATE_RESEARCH_004_NEXT_2000.md)** — four 500-row tables with dated source citations, low-confidence starred (★) estimates, and unresolved records.",
"",
"**[Research batch 004 report](data/DATE_RESEARCH_004_REPORT.json)** — audit totals and provenance rules.",
"",
"## Browse complete keyword tables",
"",
"| Inventory set | Added keywords | Full tables | ID range |",
"|---|---:|---|---|",
"| Original seed | 100 | [Initial historical leads](batches/BATCH_001.md) | AIH-00001–AIH-00100 |",
]
for n in range(1,5):
    label=str(n).zfill(3)
    names=[r["id"] for r in rows if r.get("inventory_batch")==label]
    lines.append("| "+label+" | 5,000 | [Browse all 5,000](batches/INVENTORY_"+label+"_5000.md) | "+names[0]+"–"+names[-1]+" |")
lines += [
"| **Total** | **20,100** | **40 full 500-row tables + original 100** | |",
"",
"**[Browse the 20,000 imported keywords in full GitHub tables](tables/README.md)**. Each of the 40 pages lists all 500 records as a table with permanent ID, term, category, subfield, and source-documented date where available; original first-use dates remain unverified.",
"",
"**[Master keyword CSV — all 20,100 records](data/KEYWORD_INVENTORY.csv)**",
"",
"## Provenance and QA",
"",
"- [Import QA — batches 001 and 002](data/INVENTORY_IMPORT_REPORT.json): original AI Glossary Reference from Hugging Face, MIT-licensed.",
"- [Import QA — batches 003 and 004](data/INVENTORY_IMPORT_REPORT_003_004.json): Computer Science Ontology (CSO), CC BY 4.0. Some terms are supporting-CS research terms, not independently verified core AI terms.",
"- [Reproducible CSO importer](scripts/import_cso_10000.py) and [table generator](scripts/build_keyword_tables.py).",
"- [Research methodology](docs/INVENTORY_FIRST_WORKFLOW.md).",
"",
"### Scope and limitations",
"",
"CSO has approximately 15,000 topics in version 3.5; older releases are broader. The import uses graph proximity to AI/ML and related areas to prioritize topics, but category labels and scope should be audited rather than treated as human-reviewed.",
"",
"Keyword IDs are permanent, never chronological ranks. Historical research follows **100 keywords per research batch**. Original first-use date fields remain blank until supported by original documents; chronological sorting is deferred until the date audit finishes.",
"",
"### Credits and licenses",
"",
"- Original AI Glossary Reference: https://huggingface.co/datasets/whoashish115/AI-Glossary-Reference (declared MIT license; terms imported into batches 001–002).",
"- Computer Science Ontology by Salatino, Thanapalasingam, Mannocci, Osborne, and Motta, and CSO contributors: https://cso.kmi.open.ac.uk/downloads (CC BY 4.0; batches 003–004). Adapted subset and derived category assignments.",
"",
]
(root/"README.md").write_text("\n".join(lines),encoding="utf-8")
print("Updated progress README with 20,100 total and complete batch links.")
