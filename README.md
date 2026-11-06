# AI Keyword Historical

> **CURRENT WORKFLOW (updated November 2026):** Build the complete **keyword inventory first**, then research the earliest documented *use of each term* in 100-keyword batches, and create the chronologically sorted export only after the research batches finish. [Read the inventory-first workflow](docs/INVENTORY_FIRST_WORKFLOW.md). The historic Batch 001 file below is an initial milestone-source index, **not** 100 verified term coinage dates. The 21,000-keyword figure is a research target, not a filled inventory.

**Inventory status:** [100 seeded keyword IDs](data/KEYWORD_INVENTORY.csv) / 21,000 targeted; earliest-use dates pending verification. 

A source-linked, chronological research catalog of AI-related terminology, methods, architectures, models, benchmarks, and foundational concepts. The long-term **working target** is ~20,000 distinct records across AI, machine learning, generative AI, agentic AI, AGI, and neighboring fields; the number is a planning estimate, not a census.

**Current total:** 100 records (Batch 001)  
**Coverage:** 1943–2024  
**Research categories:** 13

## Browse

- [Master historical registry](data/AI_KEYWORDS_MASTER.csv) — canonical, machine-readable dataset. **One record per keyword.**
- [Batch 001: all 100 entries](batches/BATCH_001.md) — human-readable, chronological table with per-keyword source links.

## Date semantics — do not conflate these

This database aims to discover **the earliest documented use of each AI term**. However, initial entries may have only a dated first-known **research publication or invention milestone**. They must never be presented as proven first usage without supporting evidence.

- `historical_anchor_date`: date on the earliest source currently attached to this record, or the originally documented research presentation. It may be a **concept milestone**, **method introduction**, **term attestation**, or **later landmark** as specified by `evidence_type`.
- `date_precision`: `year` or `day`. Do not invent month/day from a year-only source.
- `evidence_type`: what the dated source actually establishes: for example `term_attestation`, `named_method_preprint`, or `landmark_publication`.
- `research_status`: whether the source documents the term/technique, but **exhaustive exclusion of earlier appearances is still pending**.
- `historical_note`: important caveats. E.g., Turing's 1950 paper uses **imitation game**; it does not establish the first use of the later phrase “Turing test.” Similarly, **RLHF** is not asserted to have originated when work on learning from human preferences appeared.

**High-confidence origin rule:** A term's *true original date* may only be marked verified after checking the actual wording in the primary source and searching for earlier usage. When primary material is unavailable, keep the earliest-usage attribution provisional and link to the best currently accessible bibliographic evidence.

## Category counts — Batch 001

| Category | Keywords |
|---|---:|
| NLP and LLMs | 16 |
| Computer Vision | 15 |
| Machine Learning | 11 |
| Generative AI | 10 |
| AI Safety | 9 |
| Deep Learning | 8 |
| Reinforcement Learning | 8 |
| Agentic AI | 7 |
| Neural Networks | 5 |
| AI Foundations | 4 |
| Mathematics | 4 |
| AGI | 2 |
| Multimodal AI | 1 |
| **Total** | **100** |

## Ongoing batch workflow

1. Research **exactly 100 new unique keywords** for every numbered batch.
2. Check against existing names and historical aliases; avoid duplicate records when a term belongs to several fields. Choose one primary category and place other affiliations in subfield or a future cross-reference index.
3. Find original records where possible. Use publication date only at the precision justified by bibliographic evidence. An arXiv initial-submission year may precede a later conference publication.
4. Identify research category and original credited contributors. Distinguish first use of a *name* from introduction of an *idea*.
5. Append to the master CSV, sort by `historical_anchor_date` then keyword; **IDs never change**, including when older research is newly discovered.
6. Add `batches/BATCH_002.md` (then 003, ...) with new IDs, links, dates, and explicit outstanding historical uncertainties.
7. Validate: precisely 100 new IDs in the batch; no duplicate keywords; all dates parse; source URLs have valid syntax; no unsupported precise dates; retain cross-field coverage.

## Registry schema

`id, keyword, field, subfield, historical_anchor_date, date_precision, attribution, source_title, source_url, evidence_type, historical_note, research_status, batch`

**Quality limitation:** The first batch has 100 source-linked leads and initial date matching, **not 100 independently proven first-ever appearances**. Verification and correction are expected; cite primary research records and revise dates as older attestations are found.
