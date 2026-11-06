# AI Keyword Historical — Full, categorized source-backed inventory

**Current inventory: 20,100 terms**, comprising 100 early records and four source-import batches of 5,000. Target is 21,000 (planning estimate, not a known census).

> **Research status:** First-use historical dates remain unverified, and individual relevance of source-derived technical terms needs expert review. A source ontology topic is not proof that the term originated on any particular date.

## Date research progress

**[First 500 terms: historical evidence table](batches/DATE_RESEARCH_001_FIRST_500.md)** — 500 ID records and linked dated documents where found, with honest uncertainty labels.

**[Date research quality report](data/DATE_RESEARCH_001_REPORT.json)** — attached date count and outstanding investigations. Publication dates are not proven original coinage dates.

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
