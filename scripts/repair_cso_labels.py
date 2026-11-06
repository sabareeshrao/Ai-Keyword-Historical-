#!/usr/bin/env python3
"""Clean N-Triples language markers from CSO labels, preserve fixed IDs, replace collisions."""
import csv,json,re
from collections import Counter, defaultdict
from pathlib import Path
from import_cso_10000 import (
    ROOT, INV, SOURCE, VERSIONS, norm, aliases, parse_triples,
    download_zip, classify_and_rank
)
REPORT=ROOT/"data/CSO_LABEL_REPAIR_REPORT.json"

def clean_label(value):
    s=str(value or "").strip()
    s=s.strip('"').strip()
    # Some CSO CSV object literals are serialized as "label@en ." rather than "label".
    s=re.sub(r'\s*@(?:en|en-[A-Za-z]+)\s*\.?\s*$','',s,flags=re.IGNORECASE)
    s=re.sub(r'\s*@(?:en|en-[A-Za-z]+)\s*$','',s,flags=re.IGNORECASE)
    s=re.sub(r'\s+\.?\s*$','',s)
    return re.sub(r'\s+',' ',s).strip().strip('"')

def main():
    with INV.open(encoding="utf-8-sig",newline="") as f:
        reader=csv.DictReader(f)
        cols=list(reader.fieldnames or [])
        rows=list(reader)
    if len(rows)!=20100:raise ValueError("Expected 20,100 source records before repair")
    old=[x for x in rows if x.get("inventory_batch") not in ("003","004")]
    current=[x for x in rows if x.get("inventory_batch") in ("003","004")]
    if len(old)!=10100 or len(current)!=10000:raise ValueError("Batch sizes incorrect")
    assert current[0]["id"]=="AIH-10101"
    assert current[-1]["id"]=="AIH-20100"
    seen=set()
    for x in old:seen.update(aliases(x["keyword"]))

    rename_count=0;collisions=[]
    for r in current:
        cleaned=clean_label(r["keyword"])
        if cleaned!=r["keyword"]:rename_count+=1
        if not cleaned or len(cleaned)>115 or len(cleaned)<3 or aliases(cleaned)&seen:
            collisions.append((r,cleaned))
            r["keyword"]=""
            continue
        r["keyword"]=cleaned
        seen.update(aliases(cleaned))

    print("Labels cleaned",rename_count,"duplications needing replacement",len(collisions),flush=True)
    replaced=Counter()
    if collisions:
        all_names=set();all_labels={};graph=defaultdict(set);source_files=[]
        for version in VERSIONS:
            try:
                source,url=download_zip(version)
                terms,labels,children,stats=parse_triples(source)
                if len(terms)<5000:continue
                all_names.update(terms)
                all_labels.update(labels)
                for k,vs in children.items():graph[k].update(vs)
                source_files.append(url)
                if len(all_names)>=23000:break
            except Exception as e:print("Source skip",version,repr(e),flush=True)
        if len(all_names)<11000:raise RuntimeError("Unable to verify replacement candidates")
        assignment=classify_and_rank(all_names,graph)
        spare=defaultdict(list)
        for term in all_names:
            name=clean_label(all_labels.get(term,term))
            if not name or len(name)>115 or len(name)<3 or not re.search(r"[A-Za-z]",name):continue
            if aliases(name)&seen:continue
            score,field,ancestor,d=assignment.get(term.casefold(),(0,"AI-Supporting Computer Science","Computer Science",None))
            spare[field].append((-score,name.casefold(),name,ancestor))
        for field in spare:spare[field].sort()
        source_pools={f:iter([row for row in pool]) for f,pool in spare.items()}
        all_sorted=iter(sorted((x for pool in spare.values() for x in pool)))
        for r,old_clean in collisions:
            preferred=r["field"]
            pool=source_pools.get(preferred)
            selection=None
            if pool:
                for item in pool:
                    if not aliases(item[2])&seen:
                        selection=(item,preferred);break
            if not selection:
                for item in all_sorted:
                    if not aliases(item[2])&seen:
                        # recover category from source ontology ranking
                        field=assignment.get(item[2].casefold(),(0,"AI-Supporting Computer Science",None,None))[1]
                        selection=(item,field);break
            if not selection:
                raise RuntimeError("Insufficient unused sourced topics to replace duplicate labels")
            (score,_,name,ancestor),field=selection
            r["keyword"]=name
            r["field"]=field
            r["subfield"]="CSO: "+ancestor
            seen.update(aliases(name))
            replaced[preferred]+=1
    final=old+current
    if len({r["id"] for r in final})!=20100:raise ValueError("Duplicate IDs after repair")
    if len({norm(r["keyword"]) for r in final})!=20100:raise ValueError("Duplicate names after repair")
    if any(re.search(r'@en\s*\.?\s*$',r["keyword"],re.I) for r in final):
        raise ValueError("Unclean language marker")
    if any(not r["keyword"] for r in final):raise ValueError("Empty keyword")
    if any(r.get("first_use_date") for r in current):raise ValueError("Unverified date present")
    with INV.open("w",newline="",encoding="utf-8") as f:
        writer=csv.DictWriter(f,fieldnames=cols,lineterminator="\n")
        writer.writeheader();writer.writerows(final)
    report={"total":len(final),"kept_original":len(old),"new_batch_count":len(current),
            "trailing_language_markers_removed":rename_count,
            "duplicate_or_invalid_labels_replaced_with_unused_source_terms":len(collisions),
            "original_ids_preserved":True,
            "unique_normalized_names":len({norm(r["keyword"]) for r in final}),
            "all_new_dates_blank":True,
            "first_and_last_new_ids":[current[0]["id"],current[-1]["id"]],
            "replacement_field_counts":dict(replaced),
            "source":SOURCE,"license":"CC BY 4.0",
            "note":"Ontology candidate names; historical dates and fine-grained scope still require research."}
    REPORT.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report,indent=2),flush=True)

if __name__=="__main__":main()
