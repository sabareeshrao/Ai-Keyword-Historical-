# AI Keyword Historical — Source-Linked Inventory

This project catalogs AI, ML, deep learning, generative AI, agentic AI, AGI, and related technical vocabulary. The research goal is to establish the **original documented use of each term**, supported by primary historical evidence.

## Current progress — November 2026

| Metric | Verified imported quantity |
|---|---:|
| Original seeded keywords | 100 |
| Inventory Batch 001 | 5,000 |
| Inventory Batch 002 | 5,000 |
| **Total inventory terms** | **10,100** |
| Remaining to planning target of 21,000 | 10,900 |
| Source glossary entries | 10,200 |
| Removed duplicate/alias candidates | 118 |
| Historically verified first-use dates among the 10,000 new entries | **0** |

The imported 10,000 entries passed automated **unique normalized name**, stable-ID, category and source checks. Their semantic accuracy and precise historical origins remain to be reviewed individually. This count is **not** a claim that 10,100 terms have undergone expert historical verification.

## Browse

- [Canonical inventory CSV](data/KEYWORD_INVENTORY.csv) — 10,100 rows with permanent IDs, categories, source provenance, and blank date fields until verified.
- [Inventory Batch 001: 5,000](batches/INVENTORY_001_5000.md) — IDs AIH-00101 through AIH-05100.
- [Inventory Batch 002: 5,000](batches/INVENTORY_002_5000.md) — IDs AIH-05101 through AIH-10100.
- [Import audit report](data/INVENTORY_IMPORT_REPORT.json) — counts, category breakdown, duplicate exclusions and validation.
- [Inventory-first research method](docs/INVENTORY_FIRST_WORKFLOW.md) — dating workflow and permanent ID rules.
- [Earlier 100 source-linked historical milestone leads](batches/BATCH_001.md) — **not** confirmed first-ever word usages.
- [Legacy historical anchor data](data/AI_KEYWORDS_MASTER.csv) — milestone dates for original 100, **not** the canonical earliest-term-use field.
- [Importer source code](scripts/populate_inventory_10000.py) — deterministic, repeatable import process.

## Research sequence

1. Complete the inventory to approximately 21,000 genuine, distinct, AI-related terms. **Do not fabricate filler terms.**
2. Research earliest recorded use of the exact technical expression in batches of 100, including authorship, original document, evidence URL, and date precision.
3. Keep first-use dates blank rather than passing off technique invention/publication year as proof of the first-ever wording.
4. When all batches have been investigated, sort a final chronological **export** without changing any permanent IDs.

## Data source and attribution

The two 5,000-term inventory batches derive from [whoashish115/AI-Glossary-Reference](https://huggingface.co/datasets/whoashish115/AI-Glossary-Reference), which declares the dataset MIT-licensed and provides 10,200 entries in 38 source categories. Imported terms have been normalized/deduplicated against the prior 100 and recategorized at a high level; individual historical facts are **not** borrowed from its term definitions. Refer to the source for original license attribution.

## Status codes

- `unverified_first_use`: no validated original wording date.
- `in_research`: earliest-use evidence under review.
- `earliest_known_qualified`: earliest known attestation, but older usage not conclusively excluded.
- `verified_first_use`: original wording date supported by historical evidence under project review.
- `requires_review`: disputed/contradictory origin claims.

Inventory records have permanent IDs independent of chronological position. Never renumber when inserting earlier historical concepts.
