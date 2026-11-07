#!/usr/bin/env python3
"""Fill newly researched undated term IDs 12501..20100 with ★★ GUESSES.

These guessed years ARE NOT evidence of first use, publication dates of the
keyword, or independently confirmed web research. Every guess is a reproducible,
very-low-confidence proxy based on dates of other, related terms, with a range.
Original evidence fields and permanent IDs are NEVER changed.
"""
import csv,json,math,re,statistics
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MASTER=ROOT/"data/KEYWORD_INVENTORY.csv"
REPORT=ROOT/"data/UNDATED_RECOVERY_NEW_2386_REPORT.json"
INDEX=ROOT/"batches/UNDATED_RECOVERY_NEW_DOUBLE_STAR.md"
PAGES=ROOT/"batches/undated-recovery-new-double-star"
START=12501
LIMIT=20100
FIELDS=[
 "guessed_first_use_year","guess_method","guess_reason",
 "guess_year_range","guess_reference_ids","guess_reference_urls",
 "guess_confidence","date_status","display_date",
]
STOP=set("a an and as at by for from in is of on or the to with via using based method methods approach approaches application applications system systems model models algorithm algorithms research new towards towards learning machine artificial ai data science technology technologies theory techniques technique study studies analysis computational computer".split())
def tokens(value):
    words=re.findall(r"[a-z0-9]+",str(value or "").lower())
    result=[]
    for w in words:
        if w in STOP or len(w)<3:continue
        if len(w)>5 and w.endswith("ies"):w=w[:-3]+"y"
        elif len(w)>5 and w.endswith("s") and not w.endswith("ss"):w=w[:-1]
        result.append(w)
    return set(result)
def safe(x):return str(x or "").replace("|"," / ").replace("\n"," ").strip()
def year(value):
    m=re.match(r"^(18|19|20)\d\d$",str(value or ""))
    return int(m.group()) if m else None
def mid(values):
    return int(round(statistics.median(values)))
def clamp(y):
    return max(1900,min(2026,int(y)))
def main():
    with MASTER.open(encoding="utf-8-sig",newline="") as f:
        reader=csv.DictReader(f); columns=list(reader.fieldnames or []); rows=list(reader)
    assert len(rows)==20100
    assert len({r["id"] for r in rows})==20100
    for col in FIELDS:
        if col not in columns:columns.append(col)
    # Select ONLY previously unresolved records added by source research batches 010–013.
    selected=[r for r in rows if START<=int(r["id"].split("-")[-1])<=LIMIT
      and not r.get("first_use_date")
      and not r.get("historical_evidence_date")
      and not r.get("estimated_first_use_year")
      and not r.get("guessed_first_use_year")]
    selected.sort(key=lambda r:r["id"])
    prior_count=len(selected)
    assert prior_count>0,"No previously undated records left"
    # Do not fabricate source URLs: link only genuine date references for
    # DIFFERENT existing terms used as contextual anchors.
    anchor=[r for r in rows if year(r.get("historical_evidence_date"))
      and r.get("historical_evidence_url","").startswith("https://")]
    assert len(anchor)>=1000,"Too few genuine dated sources for field proxies"
    lookup={r["id"]:r for r in rows}
    ref_by_token=defaultdict(list)
    frequency=Counter()
    per_field=defaultdict(list)
    per_subfield=defaultdict(list)
    years_all=[]
    for i,r in enumerate(anchor):
        y=year(r["historical_evidence_date"])
        years_all.append(y)
        per_field[r.get("field","")].append(i)
        per_subfield[(r.get("field",""),r.get("subfield",""))].append(i)
        tt=tokens(r["keyword"])
        frequency.update(tt)
        for t in tt:ref_by_token[t].append(i)
    global_mid=mid(years_all)
    method_counts=Counter()
    p=[]
    for r in selected:
        tt=tokens(r["keyword"])
        fld=r.get("field","");sub=r.get("subfield","")
        pool=set()
        for t in tt:pool.update(ref_by_token.get(t,[]))
        scored=[]
        for idx in pool:
            parent=anchor[idx]
            pt=tokens(parent["keyword"])
            match=tt&pt
            if not match:continue
            w=sum(max(.15,math.log1p(len(anchor)/(1+frequency[t]))) for t in match)
            distance=w/max(1,sum(max(.15,math.log1p(len(anchor)/(1+frequency[t]))) for t in tt))
            score=distance + (.25 if parent.get("field")==fld else 0) + (.15 if parent.get("subfield")==sub and parent.get("field")==fld else 0)
            if score>=.25:scored.append((score,idx))
        scored.sort(key=lambda x:(-x[0],anchor[x[1]]["id"]))
        relevant=[idx for _,idx in scored[:5]]
        method="lexically_related_term_source_years" if relevant and scored[0][0]>=.60 else ""
        if not method:
            candidates=per_subfield.get((fld,sub),[])
            if len(candidates)>=3:
                method="same_subfield_source_year_median"
                # Use up to ten deterministically distributed anchors.
                relevant=candidates[:10]
            else:
                candidates=per_field.get(fld,[])
                if candidates:
                    method="same_field_source_year_median"
                    relevant=candidates[:10]
                else:
                    method="global_source_year_median"
                    relevant=[]
        yy=[year(anchor[j]["historical_evidence_date"]) for j in relevant] if relevant else [global_mid]
        guessed=clamp(mid(yy))
        # Wide interval prevents false precision, but the annual placeholder
        # is useful to the user's eventual experimental chronological ordering.
        spread=(max(yy)-min(yy)) if len(yy)>1 else 0
        halfspan=max(10 if method=="lexically_related_term_source_years" else 20,
                     int(math.ceil(spread/2)),)
        halfspan=min(60,halfspan)
        low=clamp(guessed-halfspan);high=clamp(guessed+halfspan)
        refs=[anchor[j] for j in relevant[:5]]
        r["guessed_first_use_year"]=str(guessed)
        r["guess_method"]=method
        r["guess_confidence"]="very_low"
        r["guess_year_range"]=f"{low}–{high}"
        r["guess_reference_ids"]=";".join(x["id"] for x in refs)
        r["guess_reference_urls"]=";".join(x["historical_evidence_url"] for x in refs)
        if method=="lexically_related_term_source_years":
            rationale="★★ GUESSED PLACEHOLDER, not a documented first-use year. Median dated-publication years of lexically related OTHER keywords ("+", ".join(x["id"] for x in refs)+"). These sources do NOT attest the present keyword; its actual origin may be outside the wide range."
        elif method=="same_subfield_source_year_median":
            rationale="★★ GUESSED PLACEHOLDER. Median source year of other terms in the same field/subfield, not evidence for this keyword. This historical date may be wrong."
        elif method=="same_field_source_year_median":
            rationale="★★ GUESSED PLACEHOLDER. Median publication year of OTHER keywords from the same field, not evidence for this keyword. This historical date may be wrong."
        else:
            rationale="★★ GUESSED PLACEHOLDER. Entire inventory's sourced-year median was used because no relevant field-level evidence was available. No source attests this keyword; this is highly uncertain."
        r["guess_reason"]=rationale
        r["date_status"]="guessed_double_star"
        r["display_date"]=str(guessed)+" ★★"
        assert not r.get("first_use_date") and not r.get("historical_evidence_date") and not r.get("estimated_first_use_year")
        method_counts[method]+=1
        p.append(r)
    assert len(p)==prior_count
    assert all(x["display_date"].endswith(" ★★") and x["guessed_first_use_year"] and x["guess_reason"] and x["guess_year_range"] for x in p)
    with MASTER.open("w",encoding="utf-8",newline="") as f:
        wr=csv.DictWriter(f,fieldnames=columns,lineterminator="\n");wr.writeheader();wr.writerows(rows)
    PAGES.mkdir(exist_ok=True,parents=True)
    lines=[
       "# Newly Undated Keywords — Double-Star Recovery",
       "",
       f"**{len(p):,} records previously undated among permanent IDs AIH-12501–AIH-20100 have been assigned explicitly speculative years marked ★★.**",
       "",
       "**★★ means a LOW-CONFIDENCE GUESS, not an internet-verified term date, original publication, or first historical use.** This pass uses contextual years from OTHER keywords and may be inaccurate by decades. Never remove ★★ until the specific keyword's date has real documentary evidence.",
       "",
       "Sources listed as *indirect anchors* do not mention or establish the history of the target keyword. All prior documented-source dates and single-star estimates are preserved.",
       "",
       "| Page | ID range | Entries | Complete table |","|---:|---|---:|---|"
    ]
    for i in range(0,len(p),500):
        block=p[i:i+500]
        n=i//500+1
        path=PAGES/f"page-{n:02d}.md"
        lines.append(f"| {n:02d} | {block[0]['id']}–{block[-1]['id']} | {len(block)} | [Open table](undated-recovery-new-double-star/page-{n:02d}.md) |")
        table=[
          f"# Undated Recovery ★★ — Page {n:02d}","",
          f"{len(block)} previously undated records, ordered by permanent ID. Original first-use dates remain unverified.",
          "",
          "[Back to complete recovery index](../UNDATED_RECOVERY_NEW_DOUBLE_STAR.md) | [Master CSV](../../data/KEYWORD_INVENTORY.csv)",
          "",
          "**Every ★★ date is a speculative placeholder, NOT a documented historical fact.** Source links are indirect context from OTHER terms only.",
          "",
          "| ID | Keyword | Field | Guessed year ★★ | Uncertainty range | Guess basis | Indirect anchor IDs |",
          "|---|---|---|---|---|---|---|",
        ]
        for row in block:
            table.append("| "+" | ".join([
                 row["id"],safe(row["keyword"]),safe(row["field"]),
                 safe(row["display_date"]),safe(row["guess_year_range"]),
                 safe(row["guess_method"]),safe(row["guess_reference_ids"]) or "none",
            ])+" |")
        table+=["","**Interpretation:** The actual term introduction may be far earlier or later. Detailed justification and indirect anchor URLs are preserved in the [master CSV](../../data/KEYWORD_INVENTORY.csv).",
              ""]
        path.write_text("\n".join(table)+"\n",encoding="utf-8")
        assert sum(line.startswith("| AIH-") for line in table)==len(block)
    lines+=["","## Results","",
      "| Classification | Count |","|---|---:|",
      f"| Newly assigned speculative years ★★ | {len(p):,} |",
      "| Historical first-use dates verified by this pass | 0 |",
      "| Previous sourced / ★ estimated dates overwritten | 0 |","",
      "### Guess provenance",""]
    for k,v in sorted(method_counts.items()):
        lines.append(f"- {k}: **{v:,}** keywords.")
    lines+=["","Do not cite a ★★ year as a date of coinage. Direct primary-source research is still required.",""]
    INDEX.write_text("\n".join(lines)+"\n",encoding="utf-8")
    still_missing=sum(
      not (r.get("first_use_date") or r.get("historical_evidence_date")
           or r.get("estimated_first_use_year") or r.get("guessed_first_use_year"))
      for r in rows if START<=int(r["id"].split("-")[-1])<=LIMIT)
    report={
      "scope":"Additional undated entries with permanent IDs AIH-12501 through AIH-20100",
      "inventory_total":len(rows),
      "previously_missing_in_scope":prior_count,
      "guessed_double_star_added":len(p),
      "left_without_any_date_in_scope":still_missing,
      "verified_term_origin_added":0,
      "previous_dates_overwritten":0,
      "guessed_years_are_facts":False,
      "confidence":"very_low",
      "method_counts":dict(method_counts),
      "table_pages":(len(p)+499)//500,
      "historical_relevance_warning":"Every double-star year is a guessed sorting placeholder inferred from OTHER terms; no date source is cited as evidence for the keyword.",
      "note":"This run assigns low-confidence ★★ proxy years to the remaining newly researched undated entries. No new first-use evidence is established.",
    }
    assert still_missing==0
    REPORT.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False,indent=2),flush=True)
if __name__=="__main__":main()
