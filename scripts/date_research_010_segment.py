#!/usr/bin/env python3
"""Research batch 010 (IDs 12501-14500) in two 1000-ID segments.

Documented source dates are not claimed to be original word coinages.
If a closely related, not exact, title is the only plausible historical clue,
its year is an ESTIMATE and must be shown with a star in human-facing tables.
"""
import argparse,csv,json,os,re,time,unicodedata,html
from pathlib import Path
from collections import Counter
from concurrent.futures import ThreadPoolExecutor,as_completed
from urllib.parse import urlencode
from urllib.request import Request,urlopen
from urllib.error import HTTPError

ROOT=Path(__file__).resolve().parents[1]
INVENTORY=ROOT/"data/KEYWORD_INVENTORY.csv"
CONTEXT=set("ai machine learning neural intelligence language natural computer computation computing algorithm deep data system systems vision model models agent agents generative prediction classification statistics statistical training reasoning reinforcement robot robotics optimization inference network networks information processing speech software programming representation attention image images autonomous".split())
STOP=set("a an and as at by for from in is of on or the to with using via towards toward into based approach approaches methods method framework frameworks model models system systems application applications".split())
def normalize(s):
    s=unicodedata.normalize("NFKC",str(s)).lower()
    return " ".join(re.findall(r"[a-z0-9]+",html.unescape(re.sub("<[^>]+>"," ",s))))
def tok(s):
    return set(normalize(s).split())
def exact(term,title):
    a,b=normalize(term),normalize(title)
    if not a or not b:return False
    if " "+a+" " not in " "+b+" ":return False
    # Acronyms and short general words frequently collide with unrelated
    # subjects. Require explicit machine-learning/AI context in the paper title.
    if len(a.split()) == 1 and len(a) <= 8:
        domain_phrases=(
            "machine learning","deep learning","artificial intelligence",
            "neural network","language model","reinforcement learning",
            "imitation learning","computer vision","natural language processing",
            "generative adversarial","knowledge graph","transformer model",
            "image recognition","speech recognition","automated reasoning",
            "robot learning","data mining","statistical learning",
            "recommender system","representation learning","pattern recognition",
            "information retrieval","computer science","artificial neural",
            "generative ai","medical ai","multi agent","multiagent",
        )
        if not any(phrase in b for phrase in domain_phrases):return False
    return True
def estimate_match(term,title):
    a=tok(term)-STOP
    b=tok(title)-STOP
    if not a or not b:return False
    # A related paper can motivate a tentative estimate ONLY when all substantial
    # term words occur in its title and their exact phrase was not found.
    if len(a)<2 or not a.issubset(b):return False
    if len(a)==2 and not ((b-a)&CONTEXT):return False
    if len(normalize(term).split()) == 1:return False
    # Merely sharing a few generic English words is not sufficient grounds
    # for even a starred date estimate. Require explicit technical context.
    if not ((b-a)&CONTEXT) and not any(
        phrase in normalize(title) for phrase in
        ("artificial intelligence","machine learning","neural network",
         "natural language processing","reinforcement learning","computer vision",
         "representation learning","computer science","deep learning")):
        return False
    return not exact(term,title)
def date_year(item):
    for k in ("issued","published","published-online","published-print"):
        x=(item.get(k) or {}).get("date-parts") or []
        if x and x[0]:
            y=x[0][0]
            if isinstance(y,int) and 1800<=y<=2026:return y
    return None
def fetch_json(url):
    req=Request(url,headers={"User-Agent":"AIKeywordHistoricalResearch/1.0 (+https://github.com/sabareeshrao/Ai-Keyword-Historical-)","Accept":"application/json"})
    for attempt in range(3):
        try:
            with urlopen(req,timeout=28) as r:return json.load(r)
        except HTTPError as e:
            if e.code not in (429,500,502,503,504):break
            time.sleep(1.5*(attempt+1))
        except Exception:
            time.sleep(attempt+1)
    return None
def crossref(term):
    url="https://api.crossref.org/works?"+urlencode({
       "query.bibliographic":term,"rows":65,
       "select":"DOI,title,issued,published,published-print,published-online,author"
    })
    d=fetch_json(url)
    if d is None:return None,True
    matches=[]
    for p in d.get("message",{}).get("items",[]):
        title=(p.get("title") or [""])[0]
        y=date_year(p)
        doi=p.get("DOI")
        if not y or not doi or not exact(term,title):continue
        authors="; ".join((" ".join([a.get("given",""),a.get("family","")])).strip() for a in p.get("author",[])[:3])
        matches.append((y,title,"https://doi.org/"+doi,authors))
    if not matches:return None,False
    y,title,source,authors=min(matches,key=lambda x:(x[0],len(x[1])))
    return {"historical_evidence_date":str(y),
            "historical_evidence_type":"crossref_exact_title_attestation",
            "historical_evidence_title":title,
            "historical_evidence_url":source,
            "historical_evidence_authors":authors,
            "historical_evidence_notes":"Dated exact-term scholarly title among search hits; not proven historical first use."},False
def openalex(term):
    url="https://api.openalex.org/works?"+urlencode({
        "search":term,"per_page":80,
        "select":"id,title,publication_year,doi,authorships"
    })
    d=fetch_json(url)
    if d is None:return None,None,True
    exacts=[];close=[]
    for p in d.get("results",[]):
        title=p.get("title") or ""
        y=p.get("publication_year")
        source=p.get("doi") or p.get("id")
        if not isinstance(y,int) or not(1800<=y<=2026) or not(source or "").startswith("https://"):continue
        authors="; ".join((a.get("author") or {}).get("display_name","") for a in p.get("authorships",[])[:3])
        if exact(term,title):exacts.append((y,title,source,authors))
        elif estimate_match(term,title):close.append((y,title,source,authors))
    if exacts:
        y,title,source,authors=min(exacts,key=lambda x:(x[0],len(x[1])))
        return {"historical_evidence_date":str(y),
                "historical_evidence_type":"openalex_exact_title_attestation",
                "historical_evidence_title":title,
                "historical_evidence_url":source,
                "historical_evidence_authors":authors,
                "historical_evidence_notes":"Exact-term title in OpenAlex search results; not proven historical first use."},None,False
    if close:
        y,title,source,authors=min(close,key=lambda x:(x[0],len(x[1])))
        estimate={
            "estimated_first_use_year":str(y),
            "estimated_source_url":source,
            "estimated_source_title":title,
            "estimated_reason":"Tentative year inferred from a related scholarly paper whose title shares all significant keyword terms but not the exact phrase. This is NOT a verified original-use date.",
            "estimated_confidence":"low",
        }
        return None,estimate,False
    return None,None,False
def process(row):
    term=row["keyword"]
    old,err_cross=crossref(term)
    if old:return {"id":row["id"],"evidence":old,"estimate":None,"crossref_error":False,"openalex_error":False}
    newer,estimate,err_open=openalex(term)
    return {"id":row["id"],"evidence":newer,"estimate":estimate,
            "crossref_error":err_cross,"openalex_error":err_open}
def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--start",type=int,required=True,choices=[12501,13501])
    args=parser.parse_args()
    with INVENTORY.open(encoding="utf-8-sig",newline="") as f:
        r=csv.DictReader(f)
        rows=list(r)
    assert len(rows)==20100
    target=sorted((r for r in rows if args.start<=int(r["id"].split("-")[-1])<args.start+1000),key=lambda r:r["id"])
    assert len(target)==1000 and target[0]["id"]==f"AIH-{args.start:05d}"
    assert all(not r.get("first_use_date") for r in target)
    assert all(not r.get("historical_evidence_date") for r in target), "Already studied; do not overwrite"
    output=[]
    with ThreadPoolExecutor(max_workers=16) as pool:
        work={pool.submit(process,r):r["id"] for r in target}
        for n,f in enumerate(as_completed(work),1):
            try:output.append(f.result())
            except Exception as e:
                output.append({"id":work[f],"evidence":None,"estimate":None,
                               "crossref_error":True,"openalex_error":True,
                               "error":str(e)[:200]})
            if n%100==0:print(f"{args.start}: processed {n}/1000",flush=True)
    output.sort(key=lambda p:p["id"])
    assert len(output)==1000 and len(set(p["id"] for p in output))==1000
    stats=Counter("documented" if p["evidence"] else "estimated_star" if p["estimate"] else "unresolved" for p in output)
    result={"start":args.start,"end":args.start+999,"results":output,
            "stats":dict(stats),
            "note":"Documented source dates are NOT verified historical first uses. Estimated dates must always display with a star."}
    dest=ROOT/"data"/f"segment_date_010_{args.start:05d}.json"
    dest.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("DONE",json.dumps({"start":args.start,**stats}),flush=True)
if __name__=="__main__":main()
