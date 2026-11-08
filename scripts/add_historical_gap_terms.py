#!/usr/bin/env python3
"""Append ONLY genuinely missing candidates spanning early computation to 2026.

Historical gap candidates have supporting era/publication sources, but their
source dates are NOT verified first occurrences of the exact keyword.
All additions use ★ and preserve the first-use field as blank. Existing IDs,
all existing columns, and all 20,100 original records remain unchanged.
"""
import csv,json,re,unicodedata
from pathlib import Path
from collections import Counter
ROOT=Path(__file__).resolve().parents[1]
MASTER=ROOT/"data/KEYWORD_INVENTORY.csv"
SOURCE=ROOT/"data/HISTORICAL_GAP_CANDIDATES_2026.tsv"
REPORT=ROOT/"data/HISTORICAL_GAP_AUDIT_REPORT.json"
INDEX=ROOT/"batches/HISTORICAL_GAP_ADDITIONS.md"
def normalize(v):
    s=unicodedata.normalize("NFKC",str(v or "")).casefold().strip()
    s=re.sub(r"\s*[\(\[][A-Z]{2,12}[\)\]]\s*$","",s)
    return re.sub(r"[^a-z0-9]+","",s.replace("τ","tau").replace("²","2"))
def clean(v):return str(v or "").replace("|"," / ").replace("\n"," ").strip()
def main():
    with MASTER.open(encoding="utf-8-sig",newline="") as f:
        dr=csv.DictReader(f);cols=list(dr.fieldnames);rows=list(dr)
    assert len(rows)>=20100 and len({r["id"] for r in rows})==len(rows)
    originals={r["id"] for r in rows if int(r["id"].split("-")[-1])<=20100}
    assert originals=={f"AIH-{n:05d}" for n in range(1,20101)}
    existing={normalize(r["keyword"]):r["id"] for r in rows}
    assert all(existing)
    with SOURCE.open(encoding="utf-8",newline="") as f:
        candidate=list(csv.DictReader(f,delimiter="\t"))
    assert len(candidate)>=180
    for f in ("historical_evidence_date","estimated_first_use_year","estimated_source_url","estimated_source_title",
              "estimated_reason","estimated_confidence","date_status","display_date","guessed_first_use_year"):
        if f not in cols:cols.append(f)
    maxid=max(int(r["id"].split("-")[-1]) for r in rows)
    added=[];skipped=[];source_counts=Counter();eras=Counter()
    for c in candidate:
        term=clean(c["keyword"]); key=normalize(term)
        assert term and key and len(term)>=3
        y=int(c["year"]); assert 1800<=y<=2026
        url=c["reference"].strip()
        assert url.startswith(("https://doi.org/","https://arxiv.org/","https://ijcai.org/","https://dspace.mit.edu/","https://www.anthropic.com/","https://developers.googleblog.com/","https://openai.com/","https://www.microsoft.com/","https://papers.nips.cc/"))
        if key in existing:
            skipped.append({"keyword":term,"duplicate_of":existing[key]})
            continue
        maxid+=1
        term_id=f"AIH-{maxid:05d}"
        row={k:"" for k in cols}
        row.update({
           "id":term_id,
           "keyword":term,
           "field":clean(c["field"]),
           "subfield":"Historical / modern terminology gap audit",
           "inventory_batch":"005",
           "estimated_first_use_year":str(y),
           "estimated_source_url":url,
           "estimated_source_title":"Historical-era source or related method milestone; see reference URL",
           "estimated_reason":"★ APPROXIMATE RESEARCH-MILESTONE YEAR, NOT VERIFIED FIRST USE OF EXACT PHRASE. "+
                      clean(c["context_note"])+" Source may support a family of techniques rather than literal keyword wording.",
           "estimated_confidence":"low",
           "date_status":"estimated_star",
           "display_date":str(y)+" ★",
        })
        assert not row.get("first_use_date") and not row.get("historical_evidence_date")
        rows.append(row)
        added.append(row)
        existing[key]=term_id
        source_counts[c["field"]]+=1
        eras["before_1960" if y<1960 else "1960_1989" if y<1990 else "1990_2019" if y<2020 else "2020_2026"]+=1
    assert len({r["id"] for r in rows})==len(rows)
    assert len({normalize(r["keyword"]) for r in rows})==len(rows),"Normalized duplicate introduced"
    assert 0<len(added)<=400,"Expected only a small gap append so chronology still has 41 pages"
    with MASTER.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=cols,lineterminator="\n");w.writeheader();w.writerows(rows)
    added.sort(key=lambda r:(int(r["estimated_first_use_year"]),r["keyword"].casefold()))
    out=[
      "# Historical and modern AI keyword gap additions","",
      f"**{len(added)} missing terms added after comparing {len(candidate)} cross-era candidates against the existing {len(rows)-len(added):,}-term master inventory.**",
      "",
      "Years marked ★ are approximate supporting-research publication/milestone years, NOT independently verified first use of the exact keyword. The reference may describe a broader term family. No ★★ date was fabricated for new terms.",
      "",
      "| Year | Keyword | Field | Reference |","|---|---|---|---|",
    ]
    for r in added:
        out.append("| "+" | ".join([r["display_date"],clean(r["keyword"]),clean(r["field"]),f"[Related research]({r['estimated_source_url']})"])+" |")
    out += ["","## Audit","",f"- Candidates examined: {len(candidate)}",f"- Newly added: {len(added)}",f"- Existing matches skipped: {len(skipped)}",
        f"- New permanent IDs: {added[0]['id']}–{maxid:05d} (assignments in insertion order; chronological sorting happens separately).",
        "- All prior IDs and original date columns preserved.",
        "- These additions were checked for normalized exact-name duplicates; near-synonyms and field relevance still benefit from expert review.",
        "",
        "[Complete master CSV](../data/KEYWORD_INVENTORY.csv) | [Chronological tables](../chronology/README.md)",""]
    INDEX.write_text("\n".join(out)+"\n",encoding="utf-8")
    report={
     "candidate_terms_checked":len(candidate),"previous_inventory":len(rows)-len(added),
     "new_keywords_added":len(added),"duplicates_skipped":len(skipped),
     "current_inventory":len(rows),"stable_original_ids_preserved":True,
     "new_keyword_ids":[r["id"] for r in rows if r.get("inventory_batch")=="005"],
     "added_by_era":dict(eras),"added_by_field":dict(source_counts),
     "skipped_sample":skipped[:45],
     "all_added_years_status":"estimated_star_related_milestone_not_first_exact_use",
     "added_verifiable_first_uses":0,
     "note":"Only normalized exact duplicates automatically skipped; reference years represent relevant historical milestone publications, not validated origin years."
    }
    REPORT.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in report.items() if k not in ("new_keyword_ids","skipped_sample","added_by_field")},indent=2),flush=True)
if __name__=="__main__":main()
