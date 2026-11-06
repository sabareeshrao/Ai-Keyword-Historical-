#!/usr/bin/env python3
"""Import 10,000 real AI terms, preserving prior stable IDs and leaving historical dates blank."""
import csv,io,json,re,unicodedata
from pathlib import Path
from collections import Counter,defaultdict,deque
from urllib.request import Request,urlopen

ROOT=Path(__file__).resolve().parents[1]
INV=ROOT/"data/KEYWORD_INVENTORY.csv"
SRC="https://huggingface.co/datasets/whoashish115/AI-Glossary-Reference"
MAP={
"Fundamentals":"AI Foundations","Symbolic AI & Reasoning":"AI Foundations",
"AI Agents":"Agentic AI","Natural Language Processing":"NLP and LLMs",
"Models & Architectures":"Deep Learning","Mathematics & Statistics":"Mathematics",
"Probabilistic Methods":"Mathematics","Optimization":"Mathematics",
"Robotics & Autonomous Systems":"Robotics","AI Ethics & Safety":"AI Safety",
"AI Policy & Governance":"AI Safety","Hardware & Compute":"AI Infrastructure",
"MLOps & Engineering":"AI Infrastructure",
}
PREF=["Machine Learning","Deep Learning","Generative AI","NLP and LLMs","Agentic AI",
"AI Foundations","Reinforcement Learning","Computer Vision","AI Safety",
"Mathematics","Robotics","AI Infrastructure"]
def download(url):
    with urlopen(Request(url,headers={"User-Agent":"AI-Keyword-History/1.0"}),timeout=120) as r:return r.read()
def terms():
    try:
        raw=download(SRC+"/resolve/main/ai_glossary.csv").decode("utf-8-sig")
        out=list(csv.DictReader(io.StringIO(raw)))
        if len(out)>=10000 and "term" in out[0] and "category" in out[0]:
            return out,"ai_glossary.csv"
    except Exception as e:print("CSV fallback:",e)
    import pyarrow.parquet as pq
    out=pq.read_table(io.BytesIO(download(SRC+"/resolve/main/data/train.parquet")),
                      columns=["id","term","category"]).to_pylist()
    if len(out)<10000:raise ValueError("Unexpected dataset size")
    return out,"data/train.parquet"
def norm(s):
    s=unicodedata.normalize("NFKC",str(s)).casefold()
    return re.sub(r"[^a-z0-9]+","",s)
def aliases(s):
    s=str(s).strip(); keys={norm(s)}
    m=re.fullmatch(r"(.+?)\s*\(([A-Za-z][A-Za-z0-9+/.-]{1,14})\)",s)
    if m:keys.update({norm(m[1]),norm(m[2])})
    return keys-{""}
def main():
    with INV.open(newline="",encoding="utf-8-sig") as f:
        reader=csv.DictReader(f)
        columns=list(reader.fieldnames or [])
        old=list(reader)
    if len(old)<100:raise ValueError("Missing original inventory")
    if "inventory_batch" not in columns:columns.append("inventory_batch")
    cnt=Counter(r.get("inventory_batch") for r in old)
    if cnt["001"]==5000 and cnt["002"]==5000:
        print("Two 5000-record batches already present");return
    if cnt["001"] or cnt["002"]:raise ValueError("Partial batch detected; refusing renumber")
    for r in old:r["inventory_batch"]=r.get("inventory_batch") or "000"
    seen=set()
    for r in old:seen.update(aliases(r["keyword"]))
    raw,source_path=terms()
    cat=defaultdict(list); excluded=Counter()
    for r in raw:
        name=str(r.get("term","")).strip()
        group=str(r.get("category","")).strip()
        if not name or not group or len(name)>140:
            excluded["empty_or_invalid"]+=1;continue
        keys=aliases(name)
        if keys & seen:
            excluded["duplicate_or_alias"]+=1;continue
        seen.update(keys)
        cat[group].append(name)
    available=sum(map(len,cat.values()))
    if available<10000:
        raise ValueError(f"Only {available} source-backed unique terms; need 10000. No fillers added.")
    ordered=sorted(cat,key=lambda x:(PREF.index(MAP.get(x,x)) if MAP.get(x,x) in PREF else 100,x))
    dq={k:deque(sorted(v,key=str.casefold)) for k,v in cat.items()}
    selected=[]
    while len(selected)<10000:
        for category in ordered:
            if dq[category]:
                selected.append((dq[category].popleft(),category))
                if len(selected)==10000:break
    max_id=max(int(r["id"].split("-")[-1]) for r in old)
    new=[]
    for i,(keyword,category) in enumerate(selected):
        new.append(dict(id=f"AIH-{max_id+i+1:05d}",keyword=keyword,
            field=MAP.get(category,category),subfield=category,
            first_use_date="",first_use_evidence="",research_status="unverified_first_use",
            seed_source=SRC+"/tree/main/"+source_path,historical_reference="",
            inventory_batch="001" if i<5000 else "002"))
    merged=old+new
    if len({r["id"] for r in merged})!=len(merged):raise ValueError("ID collision")
    if len({norm(r["keyword"]) for r in merged})!=len(merged):raise ValueError("Name collision")
    with INV.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=columns,lineterminator="\n")
        w.writeheader();w.writerows(merged)
    bdir=ROOT/"batches";bdir.mkdir(exist_ok=True)
    for number,group in [(1,new[:5000]),(2,new[5000:])]:
        stats=Counter(r["field"] for r in group)
        heading=f"Inventory Batch {number:03d} — 5000 keywords"
        text=[f"# {heading}","",
              "Inventory terms only: historical first-use dates remain blank.","",
              f"Source: {SRC} (MIT-licensed dataset)","",
              f"Stable IDs: {group[0]['id']} through {group[-1]['id']}","",
              "All records: ../data/KEYWORD_INVENTORY.csv","",
              "| Category | Count |","|---|---:|"]
        text += [f"| {k} | {v} |" for k,v in sorted(stats.items())]
        text += ["","## Example terms","","| ID | Term | Category |","|---|---|---|"]
        text += [f"| {r['id']} | {r['keyword'].replace('|','/')} | {r['field']} |" for r in group[:35]]
        (bdir/f"INVENTORY_{number:03d}_5000.md").write_text("\n".join(text)+"\n",encoding="utf-8")
    report={"previous_total":len(old),"added":len(new),"inventory_total":len(merged),
            "batch_001":5000,"batch_002":5000,"source_rows":len(raw),
            "source_terms_after_dedup":available,"source":SRC,"source_file":source_path,
            "excluded":dict(excluded),"dates_blank":True,"distinct_ids":len(merged),
            "distinct_normalized_names":len({norm(r["keyword"]) for r in merged}),
            "batch_001_first":new[0]["id"],"batch_001_last":new[4999]["id"],
            "batch_002_first":new[5000]["id"],"batch_002_last":new[-1]["id"],
            "categories":dict(Counter(r["field"] for r in new))}
    (ROOT/"data/INVENTORY_IMPORT_REPORT.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report,indent=2))
if __name__=="__main__":main()
