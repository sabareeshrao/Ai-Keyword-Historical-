# Inventory-first historical research workflow

## Current direction

**Phase A — Inventory.** Collect up to **21,000 genuine distinct AI-relevant keywords** before spending time researching their original historical dates. 21,000 is a planning target, **not a verified count**, so the final number may be smaller or larger. Reject invented filler, duplicate names, and entries unrelated to AI or its directly supporting fields.

**Phase B — Historical annotation.** Once the unique keyword inventory is established, work in locked blocks of **100 inventory IDs per batch**. For each, establish **earliest documented original use of the expression** if supported, with author, original publication, evidence, and date precision. Preserve uncertainty where earlier usage has not been excluded.

**Phase C — Final chronology.** Once historical research is complete, create sorted views (ascending by verified earliest-usage date, then keyword). **Never renumber IDs.** Sorting before completion is not required and must not change the inventory's permanent ID order.

## Files

- `data/KEYWORD_INVENTORY.csv` — **canonical keyword inventory**. It contains stable ID, term, field, subfield, first-use date (empty until verified), evidence, research status, seed source, and reference to historical research.
- `data/AI_KEYWORDS_MASTER.csv` — original Batch 001 historical **source-anchor leads**. These are useful starting sources, **not 100 independently verified first-ever term appearances**.
- `batches/BATCH_001.md` — readable historical leads from the original approach. Retain for auditability.
- Future `batches/RESEARCH_001.md`, `RESEARCH_002.md`, etc. will provide the completed origin research for each fixed group of 100 inventory IDs.
- After completing all batches, produce `exports/KEYWORDS_SORTED_BY_ORIGIN.csv` with immutable IDs.

## Suggested authoritative seeds

- Computer Science Ontology v3.5: https://cso.kmi.open.ac.uk/downloads — approx. 15,000 broad CS topics; **must filter and classify** for AI relevance. Licensing: CC BY 4.0. Credit original CSO authors and comply with the license.
- AI Glossary Reference: https://huggingface.co/datasets/whoashish115/AI-Glossary-Reference — describes 10,200 AI/ML terms, 38 categories. Review dataset license and content accuracy **before reusing**.
- Google ML Glossary: https://developers.google.com/machine-learning/glossary — terminology cross-check, not blanket permission for bulk redistribution.

**Source entry rule:** Each imported keyword should identify its dataset/source and have a real category. Retain a provenance record. A source-term count does not equal a unique, AI-relevant count after deduplication.

## Data semantics

- `first_use_date` in `KEYWORD_INVENTORY.csv` means **date of first documented use of the exact term in an AI-relevant sense**. It stays blank until verified.
- `historical_anchor_date` in legacy `AI_KEYWORDS_MASTER.csv` is merely the date of an identified publication or method milestone and must not be silently migrated into `first_use_date`.
- Valid `research_status` values: `unverified_first_use`, `in_research`, `verified_first_use`, `earliest_known_qualified`, `requires_review`.
- Store **year-only dates as years**. Never invent January 1 as if an unknown exact date were known.
- Distinguish an invention/method's first publication from the coined wording. Document conflicts when researchers dispute origins.

## Stable-ID and batch rules

1. Normalize Unicode, whitespace and capitalization for duplicate checking, while preserving preferred display names.
2. Merge spelling variants, synonyms, and acronym expansions where they mean the same concept; keep meaningful distinct methods as separate records.
3. Add new IDs only for genuinely new terms, never reorder or reuse IDs.
4. An `AIH-xxxxx` ID is an identity key, **not an ordinal historical rank**.
5. Research exactly 100 stable IDs per batch, ideally in ID sequence, excluding already verified IDs. Report how many records remain unresearched.
6. Generate the final historical order **only once all selected terms are verified or explicitly marked as unresolved**, with unresolved terms grouped separately.
7. Maintain a change log whenever an earlier source changes a previously recorded date.

## Honest progress accounting

The inventory currently has only the **100 original records**. No one has yet imported and vetted the remaining ~20,900 candidate terms. Do not label the 21,000-target inventory as complete until the file truly contains 21,000 qualified unique entries and has passed name/category/provenance validation.
