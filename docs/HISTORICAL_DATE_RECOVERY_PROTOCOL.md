# Historical-date recovery protocol — 2026-11-06

## Reason title-only search failed

Previous scripts queried 70 Crossref and 60 OpenAlex **relevance-ranked title matches**, so non-titular terms and many historically older documents were missed. A blank simply meant the selected API result windows did not contain an exact title; it did **not** mean that a term lacked historical evidence.

OpenAlex and Crossref documentation:

- https://help.openalex.org/api/searching/
- https://www.crossref.org/documentation/retrieve-metadata/rest-api/
- https://github.com/CrossRef/rest-api-doc

## Evidence ladder: each term gets multiple passes

1. **Original method/term title and paper:** Search the exact phrase and variants in arXiv, ACL Anthology, PMLR, journals, and primary proceedings. Use earliest original preprints when dated; do not substitute conference year if a valid earlier release exists.
2. **Dated wording in abstracts/full text:** Search both Crossref and OpenAlex; use date-ascending result windows plus relevance windows. Re-check the *exact occurrence and its AI meaning* in the source; title-only matching has poor recall. Archived manuals, technical reports, books, and old conference material may predate the earliest indexed work.
3. **Dated technical documentation:** For tools and organizations, use first release, founding announcement, documentation history, or archived source code; mark concept/method/organization founding separately from the first exact term use.
4. **Historical predecessor chain:** When the exact expression is newer or cannot be found, document the earliest predecessor, later distinctive method, and first firmly known mention. A method's original publication is **not** automatically the eponym's coinage.
5. **Reasoned estimate (★):** Only when the history supports a defensible year/range; record the numeric year in `historical_date`, `date_status=estimated`, `is_estimated=true`, and display `YYYY ★`. Explain whether this is a method/organization-anchored proxy rather than first wording. Confidence Low/Medium. No arbitrary default year.
6. **Genuine unknown:** If no anchored inference survives critical review, leave `historical_date` blank and label `unresolved`. Do not fabricate dates for novel/compound administrative phrases; a blank is better than false history.

## Controlled candidate collection

Run the versioned discovery script (standard library only):

```bash
python scripts/recovery_evidence_discovery.py --limit 100 --workers 3
```

It reads the **existing GitHub CSV**, searches Crossref and OpenAlex for phrase matches in **titles or abstracts**, considers date-sorted OpenAlex results, and writes the five earliest metadata leads per keyword to `data/RECOVERY_004_CANDIDATES.csv`. It never modifies the canonical inventory automatically or asserts original first use. The candidate output must undergo an original-source and date-precision check before adding any term dates.

A workflow is available under GitHub Actions as **Historical candidate discovery (manual)** to run this on the repository and publish a CSV research artifact without requiring locally downloaded inventory files. This stage does not mean 1,000 records have finished source verification.

## Special cases

- **Acronyms:** Verify the expansion and meaning in source context (e.g. names shared by unrelated papers). Avoid automatic exact title matching on acronyms.
- **Named eponyms:** Distinguish the original underlying work from the later name ('Benders decomposition', 'Bradley–Terry model', etc.).
- **Component/composite terms:** These might be glossary label combinations rather than historically coined phrases. Report the closest predecessor and exact-phrase first-attestation separately.
- **Date ranges:** Preserve both earliest attested year and lower-bound evidence, if available. A lower bound from concept history is not a legal proof that the expression could not predate it.
- **First-ever claim:** The absence of an older indexed result is not evidence no earlier use existed. `earliest_known` must be qualified.
- **Cost/time:** Query in controlled groups, cache results when possible, back off on 429s, and inspect candidate quality before expanding to the remaining 17,600.

## QA before any date write

Check 20,100 unique immutable IDs; unchanged original 16 CSV fields unless a source-correction change log supports a revision; original 1,350 source dates retained; every new year has a source and rationale; every estimate displays ★ but numeric fields do not; candidate counts never get reported as finished historical research. Two 500-row tables must reflect the final reviewed changes, not merely proposed dates.
