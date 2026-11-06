#!/usr/bin/env python3
"""Research a source-documented date for first 500 terms.
A document date is never asserted to be the first-ever use of the expression.
"""
import csv, json, re, time, html, unicodedata
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import Counter
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request,urlopen
from urllib.error import HTTPError

root=Path(__file__).resolve().parents[1]
master=root/"data/KEYWORD_INVENTORY.csv"
original=root/"data/AI_KEYWORDS_MASTER.csv"
report_path=root/"data/DATE_RESEARCH_001_REPORT.json"
index_path=root/"batches/DATE_RESEARCH_001_FIRST_500.md"
cols_add=["historical_evidence_date","historical_evidence_type","historical_evidence_title",
          "historical_evidence_url","historical_evidence_authors","historical_evidence_notes"]
CONTEXT=set("artificial ai intelligence learning neural machine data algorithms algorithm model models network networks computer computing software language robotics robot deep statistics statistical system systems optimization prediction classification information image speech internet generative inference agent agents evaluation simulation recognition mathematical computation training reasoning".split())

def norm(v):
    s=unicodedata.normalize("NFKC",str(v)).lower()
    return re.sub(r"\s+"," ",re.sub(r"[^a-z0-9]+"," ",s)).strip()

def exact_title(term,title):
    t=norm(html.unescape(re.sub(r"<[^>]+>"," ",title)))
    k=norm(term)
    if not k or not t or (" "+k+" ") not in (" "+t+" "):return False
    if len(k.split())==1 and len(k)<8:
        if not (set(t.split())-{k})&CONTEXT:return False
    return True

def year(item):
    for field in ("issued","published","published-online","published-print"):
        x=(item.get(field) or {}).get("date-parts") or []
        if x and x[0]:
            y=x[0][0]
            if isinstance(y,int) and 1800<=y<=2026:return str(y)
    return ""

def lookup(keyword):
    params=urlencode({"query.bibliographic":keyword,"rows":70,
                      "select":"DOI,title,issued,published,published-print,published-online,author"})
    url="https://api.crossref.org/works?"+params
    req=Request(url,headers={"User-Agent":"AI-Historical-Keyword-Research/1.0 (GitHub: sabareeshrao/Ai-Keyword-Historical-)","Accept":"application/json"})
    for attempt in range(3):
        try:
            with urlopen(req,timeout=35) as r:
                result=json.load(r)
            matches=[]
            for item in result.get("message",{}).get("items",[]):
                title=(item.get("title") or [""])[0]
                if not exact_title(keyword,title):continue
                y=year(item);doi=item.get("DOI","")
                if not y or not doi:continue
                authors=[" ".join([a.get("given",""),a.get("family","")]).strip()
                         for a in item.get("author",[])[:3]]
                matches.append((int(y),title,doi,"; ".join(authors)))
            if not matches:return ("","unresolved","","","","No exact-title attestation found in selected Crossref results.")
            y,t,doi,authors=min(matches,key=lambda x:(x[0],len(x[1])))
            return (str(y),"crossref_exact_title_attestation",t,"https://doi.org/"+doi,authors,
                    "Earliest matching title among 70 retrieved Crossref results, not earliest known historical wording.")
        except HTTPError as e:
            if attempt<2 and e.code in (429,500,502,503,504):
                time.sleep(2+attempt*3);continue
            return ("","search_error","","","","Crossref HTTP "+str(e.code))
        except Exception as e:
            if attempt<2:time.sleep(1+attempt);continue
            return ("","search_error","","","","Crossref error "+type(e).__name__)
    return ("","search_error","","","","No response")

def main():
    with master.open(encoding="utf-8-sig",newline="") as f:
        r=csv.DictReader(f);header=list(r.fieldnames);records=list(r)
    with original.open(encoding="utf-8-sig",newline="") as f:
        legacy={r["id"]:r for r in csv.DictReader(f)}
    assert len(records)==20100 and len(legacy)==100
    target=sorted([r for r in records if int(r["id"].split("-")[-1])<=500],key=lambda r:r["id"])
    assert len(target)==500 and target[0]["id"]=="AIH-00001" and target[-1]["id"]=="AIH-00500"
    for col in cols_add:
        if col not in header:header.append(col)
    for r in target[:100]:
        src=legacy[r["id"]]
        assert norm(r["keyword"])==norm(src["keyword"])
        info=(src["historical_anchor_date"],"legacy_milestone_not_first_use",
              src["source_title"],src["source_url"],src["attribution"],
              src["historical_note"]+"; earliest exact expression not proven.")
        r.update(dict(zip(cols_add,info)))
    print("100 milestone sources loaded",flush=True)
    findings={}
    with ThreadPoolExecutor(max_workers=6) as pool:
        futures={pool.submit(lookup,r["keyword"]):r["id"] for r in target[100:]}
        for i,future in enumerate(as_completed(futures),1):
            uid=futures[future]
            try:findings[uid]=future.result()
            except Exception as e:findings[uid]=("","search_error","","","",str(e)[:100])
            if i%50==0:print("Searched",i,"of 400",flush=True)
    for r in target[100:]:
        r.update(dict(zip(cols_add,findings[r["id"]])))
        assert not r.get("first_use_date"), "Automated title matches cannot establish first-ever terminology."
    with master.open("w",encoding="utf-8",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=header,lineterminator="\n")
        writer.writeheader();writer.writerows(records)
    counts=Counter(r["historical_evidence_type"] for r in target)
    out=["# First 500 Keywords — Documented Historical Date Research","",
        "**Exactly 500 entries** (AIH-00001 through AIH-00500).",
        "",
        "**DATE WARNING:** These are documented publication years or dates of cited historical milestones. They are NOT verified first-ever use dates of the specific terminology. Exact term origination requires separate original-text research.",
        "",
        "An em dash means no credible dated source was located from this search. The verified first-use date column in the master CSV remains blank.",
        "",
        "| ID | Keyword | Category | Source-documented date | Original evidence | Evidence status |",
        "|---|---|---|---|---|---|"]
    for r in target:
        status={"legacy_milestone_not_first_use":"Legacy milestone (term origin unverified)",
                "crossref_exact_title_attestation":"Exact title attestation (origin unverified)",
                "unresolved":"No exact-title result","search_error":"Search unavailable"}.get(r["historical_evidence_type"],"Unknown")
        link=("[Paper]("+r["historical_evidence_url"]+")" if r.get("historical_evidence_url") else "—")
        fields=[r["id"],r["keyword"].replace("|","/"),r["field"].replace("|","/"),
                r.get("historical_evidence_date") or "—",link,status]
        out.append("| "+" | ".join(fields)+" |")
    dated=sum(bool(r.get("historical_evidence_date")) for r in target)
    out+=["","## Quality report","",
          "| Metric | Count |","|---|---:|",
          "| Keywords reviewed | 500 |",
          f"| Source-documented dates attached | {dated} |",
          "| Existing milestone sources | 100 |",
          f"| Additional exact-title references | {counts['crossref_exact_title_attestation']} |",
          f"| Unresolved title searches | {counts['unresolved']} |",
          f"| Retrieval failures | {counts['search_error']} |",
          "| Historically verified original word-use dates | 0 |",
          "",
          "Method: Crossref metadata bibliographic search; require exact normalized keyword in publication title. Select earliest dated match from up to 70 relevance-ranked titles. This does not prove the first occurrence in all literature.",
          "",
          "[Machine-readable master data](../data/KEYWORD_INVENTORY.csv) · [Report JSON](../data/DATE_RESEARCH_001_REPORT.json)"]
    index_path.write_text("\n".join(out)+"\n",encoding="utf-8")
    report={"examined":500,"id_range":["AIH-00001","AIH-00500"],
            "existing_milestone_dates":100,
            "additional_crossref_title_dates":counts["crossref_exact_title_attestation"],
            "unresolved":counts["unresolved"],"search_error":counts["search_error"],
            "dated_total":dated,"verified_original_term_first_uses":0,
            "provisional_dates_not_origin_proof":True,
            "all_permanent_ids_preserved":True,"inventory_total":len(records)}
    report_path.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report,indent=2),flush=True)
if __name__=="__main__":main()
