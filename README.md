# AI Keyword Historical — Full, categorized source-backed inventory

**Current inventory: 20,100 terms**, comprising 100 early records and four source-import batches of 5,000. Target is 21,000 (planning estimate, not a known census).

> **Research status:** First-use historical dates remain unverified, and individual relevance of source-derived technical terms needs expert review. A source ontology topic is not proof that the term originated on any particular date.

## Concurrent recovery research (separate series)

**[Recovery 004: first 1,000 previously unresolved records](batches/DATE_RESEARCH_004_RECOVERY_FIRST_1000.md)** — separate recovery project, 25 independently reviewed dated leads (23 references + 2 ★ estimates), 975 pending. This work is preserved and not overwritten by the new 2,000-ID research batch.

**[Recovery 004 QA report](data/DATE_RESEARCH_004_REPORT.json)** — 25 reviews and status of remaining unresolved terms.

## Date research progress

**[First 500 terms: historical evidence table](batches/DATE_RESEARCH_001_FIRST_500.md)** — 500 ID records and linked dated documents where found, with honest uncertainty labels.

**[Date research quality report](data/DATE_RESEARCH_001_REPORT.json)** — attached date count and outstanding investigations. Publication dates are not proven original coinage dates.

**[Next 1,000 term-date research (IDs AIH-00501 to AIH-01500)](batches/DATE_RESEARCH_002_NEXT_1000.md)** — two full 500-row tables, linked source-documented dates, and unresolved statuses.

**[Research batch 002 JSON report](data/DATE_RESEARCH_002_REPORT.json)** — dated and unresolved totals.

**[Date research 003: Next 1,000 terms (AIH-01501–AIH-02500)](batches/DATE_RESEARCH_003_NEXT_1000.md)** — two full 500-row tables with cited source dates. These are not proven term-origin dates.

**[Date research 003 audit](data/DATE_RESEARCH_003_REPORT.json)** — count of retrieved dates and unresolved terms.

**[Date research 005: 2,000 keywords (AIH-02501–AIH-04500)](batches/DATE_RESEARCH_005_NEXT_2000.md)** — four 500-row tables with dated source citations, low-confidence starred (★) estimates, and unresolved records.

**[Research batch 005 report](data/DATE_RESEARCH_005_REPORT.json)** — audit totals and provenance rules.

**[Date research 006: Next 2,000 keywords (AIH-04501–AIH-06500)](batches/DATE_RESEARCH_006_NEXT_2000.md)** — four full 500-row tables with dated publications, estimated years ★, and unresolved records.
**[Research batch 006 QA report](data/DATE_RESEARCH_006_REPORT.json)** — actual counts, source status, and evidence limitations.
**[Date research 007: Next 2,000 keywords (AIH-06501–AIH-08500)](batches/DATE_RESEARCH_007_NEXT_2000.md)** — complete 500-row pages, dated-source evidence, starred estimates, and unresolved terms.

**[Date research 007 audit](data/DATE_RESEARCH_007_REPORT.json)** — actual findings and preserved-ID checks.

**[Date research 008: 2,000 keywords (AIH-08501–AIH-10500)](batches/DATE_RESEARCH_008_NEXT_2000.md)** — four full 500-row tables with documented source dates and ★ estimates.

**[Date research 008 audit](data/DATE_RESEARCH_008_REPORT.json)** — source-date results and unresolved terms.

**[Date research 009: Next 2,000 keywords (AIH-10501–AIH-12500)](batches/DATE_RESEARCH_009_NEXT_2000.md)** — four complete 500-row tables, source-documented dates, explicitly starred estimates, and unresolved records.

**[Date research 009 QA report](data/DATE_RESEARCH_009_REPORT.json)** — source research totals and preserved-ID checks.

**[Date research 010: Next 2,000 keywords (AIH-12501–AIH-14500)](batches/DATE_RESEARCH_010_NEXT_2000.md)** — four complete 500-row tables with sourced dates, estimated years ★, and unresolved terms.

**[Date research 010 QA report](data/DATE_RESEARCH_010_REPORT.json)** — date-source counts, confidence flags, and ID-preservation checks.

## Previously undated recovery — ★★ guessed dates

**[Complete double-star recovery tables](batches/UNDATED_RECOVERY_DOUBLE_STAR.md)** — all previously undated records from AIH-00001–AIH-12500 now receive unmistakably speculative ★★ years, supporting indirect-context anchor IDs, approximate ranges, and methods. The years are guesses, NOT sourced term introductions.

**[Double-star recovery audit report](data/UNDATED_RECOVERY_DOUBLE_STAR_REPORT.json)** — exact current count and methodology breakdown.

**[Date research 011: Next 2,000 keywords (AIH-14501–AIH-16500)](batches/DATE_RESEARCH_011_NEXT_2000.md)** — four complete 500-row tables with dated scholarly sources, ★ estimates, and unresolved entries.

**[Date research 011 audit report](data/DATE_RESEARCH_011_REPORT.json)** — source-date totals and previous-ID preservation verification.

## Browse complete keyword tables

| Inventory set | Added keywords | Full tables | ID range |
|---|---:|---|---|
| Original seed | 100 | [Initial historical leads](batches/BATCH_001.md) | AIH-00001–AIH-00100 |
| 001 | 5,000 | [Browse all 5,000](batches/INVENTORY_001_5000.md) | AIH-00101–AIH-05100 |
| 002 | 5,000 | [Browse all 5,000](batches/INVENTORY_002_5000.md) | AIH-05101–AIH-10100 |
| 003 | 5,000 | [Browse all 5,000](batches/INVENTORY_003_5000.md) | AIH-10101–AIH-15100 |
| 004 | 5,000 | [Browse all 5,000](batches/INVENTORY_004_5000.md) | AIH-15101–AIH-20100 |
| **Total** | **20,100** | **40 full 500-row tables + original 100** | |

**[Browse the 20,000 imported keywords in full GitHub tables](tables/README.md)**. Each of the 40 pages lists all 500 records as a table with permanent ID, term, category, subfield, and source-documented date where available; original first-use dates remain unverified.

**[Master keyword CSV — all 20,100 records](data/KEYWORD_INVENTORY.csv)**

## Provenance and QA

- [Import QA — batches 001 and 002](data/INVENTORY_IMPORT_REPORT.json): original AI Glossary Reference from Hugging Face, MIT-licensed.
- [Import QA — batches 003 and 004](data/INVENTORY_IMPORT_REPORT_003_004.json): Computer Science Ontology (CSO), CC BY 4.0. Some terms are supporting-CS research terms, not independently verified core AI terms.
- [Reproducible CSO importer](scripts/import_cso_10000.py) and [table generator](scripts/build_keyword_tables.py).
- [Research methodology](docs/INVENTORY_FIRST_WORKFLOW.md).

### Scope and limitations

CSO has approximately 15,000 topics in version 3.5; older releases are broader. The import uses graph proximity to AI/ML and related areas to prioritize topics, but category labels and scope should be audited rather than treated as human-reviewed.

Keyword IDs are permanent, never chronological ranks. Historical research follows **100 keywords per research batch**. Original first-use date fields remain blank until supported by original documents; chronological sorting is deferred until the date audit finishes.

### Credits and licenses

- Original AI Glossary Reference: https://huggingface.co/datasets/whoashish115/AI-Glossary-Reference (declared MIT license; terms imported into batches 001–002).
- Computer Science Ontology by Salatino, Thanapalasingam, Mannocci, Osborne, and Motta, and CSO contributors: https://cso.kmi.open.ac.uk/downloads (CC BY 4.0; batches 003–004). Adapted subset and derived category assignments.
