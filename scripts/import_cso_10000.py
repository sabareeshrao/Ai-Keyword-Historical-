#!/usr/bin/env python3
"""Append up to 10,000 distinct ontology-backed topic labels without changing existing IDs.

CSO versions: https://cso.kmi.open.ac.uk/downloads  (CC BY 4.0).
Imported records are AI / ML and supporting CS research-topic candidates, not
verified original-date discoveries. Abort rather than fabricate missing terms.
"""
import csv, io, json, re, unicodedata, zipfile
from collections import Counter, defaultdict, deque
from pathlib import Path
from urllib.parse import unquote
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
INV = ROOT/"data/KEYWORD_INVENTORY.csv"
OUT = ROOT/"data/INVENTORY_IMPORT_REPORT_003_004.json"
SOURCE = "https://cso.kmi.open.ac.uk/downloads"
VERSIONS = ["3.5", "2.1", "2.0"]
TOPIC = re.compile(r"cso\.kmi\.open\.ac\.uk/topics/([^\s<>\"',;]+)", re.I)
RELS = ("supertopicof","relatedequivalent","contributesto","preferentialequivalent")
DOMAINS = [
("AI Foundations",["artificial intelligence","computational intelligence","knowledge representation","expert systems","automated reasoning","intelligent systems","knowledge engineering"]),
("Machine Learning",["machine learning","pattern recognition","data mining","statistical learning","classification","clustering","feature selection","predictive analytics"]),
("Deep Learning",["deep learning","neural networks","artificial neural networks","deep neural networks","neural network architectures"]),
("Generative AI",["generative models","generative artificial intelligence","generative adversarial networks","text generation","image generation"]),
("NLP and LLMs",["natural language processing","computational linguistics","language modeling","large language models","machine translation","text mining","information extraction"]),
("Agentic AI",["intelligent agents","multi-agent systems","software agents","autonomous agents","agent-based systems"]),
("Computer Vision",["computer vision","image processing","object recognition","image analysis","pattern analysis","visual computing"]),
("Reinforcement Learning",["reinforcement learning","decision processes","sequential decision making","game theory"]),
("Mathematics",["optimization","applied mathematics","statistics","probability theory","linear algebra","graph theory","stochastic processes"]),
("Robotics",["robotics","autonomous systems","robot navigation","control systems","motion planning"]),
("AI Infrastructure",["distributed computing","parallel computing","computer architecture","cloud computing","database systems","information systems","computer networks","high performance computing","computer hardware"]),
("AI Safety",["computer security","information security","privacy","trustworthy ai","fairness","cybersecurity"]),
("Information Retrieval",["information retrieval","search engines","semantic web","knowledge graphs","ontologies"]),
("Data Science",["data science","data analysis","scientific computing","bioinformatics","data visualization"]),
("Speech & Audio",["speech recognition","audio processing","signal processing","speech synthesis"]),
("AI Applications",["medical informatics","healthcare informatics","computational biology","recommendation systems","human computer interaction"]),
("Programming & Software",["programming languages","software engineering","algorithms","data structures","software architecture","program analysis"]),
]
ANCHOR = {name.casefold(): field for field,names in DOMAINS for name in names}

def norm(x):
    x=unicodedata.normalize("NFKC",str(x)).casefold()
    return re.sub(r"[^a-z0-9]+","",x)

def aliases(x):
    s=str(x).strip()
    out={norm(s)}
    m=re.fullmatch(r"(.+?)\s*\(([A-Za-z][A-Za-z0-9+/.-]{1,14})\)",s)
    if m:out.update([norm(m[1]),norm(m[2])])
    return out-{""}

def download_zip(version):
    url="https://cso.kmi.open.ac.uk/download/version-"+version+"/CSO."+version+".csv.zip"
    req=Request(url,headers={"User-Agent":"Mozilla/5.0 (AI historical research; CSO CC-BY-4.0)"})
    with urlopen(req,timeout=100) as response:
        data=response.read()
    if data[:2]!=b"PK":
        raise ValueError("Not a ZIP file: "+url+" received "+str(data[:80]))
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        names=[n for n in z.namelist() if n.lower().endswith((".csv",".txt")) and not n.startswith("__MACOSX")]
        if not names:raise ValueError("No CSV inside "+url)
        raw=z.read(max(names,key=lambda n:z.getinfo(n).file_size))
    print("Downloaded",url,"csv bytes",len(raw),"rows approx",raw.count(b"\n"),flush=True)
    return raw.decode("utf-8-sig",errors="replace"),url

def term_of(raw):
    s=str(raw).strip().strip("<>").strip()
    m=TOPIC.search(s)
    if not m:return None
    frag=m.group(1).split("?")[0].split("#")[0].strip().strip(".")
    return unquote(frag).replace("_"," ").strip()

def parse_triples(content):
    names=set();labels={};children=defaultdict(set)
    counts=Counter()
    reader=csv.reader(io.StringIO(content))
    for row in reader:
        if len(row)<3:
            counts["short_row"]+=1;continue
        subject,predicate,obj=[str(x).strip() for x in row[:3]]
        s=term_of(subject)
        o=term_of(obj)
        if not s:continue
        names.add(s)
        p=predicate.casefold()
        if o:names.add(o)
        if "label" in p and not o:
            text=obj.strip().strip('"').split('"@')[0].strip()
            if text.startswith("http") or len(text)>120:continue
            labels[s]=text
        if "supertopicof" in p and o:
            children[s.casefold()].add(o.casefold())
            counts["hierarchy"]+=1
        counts["triples"]+=1
    return names, labels, children, counts

def classify_and_rank(names,children):
    graph=defaultdict(set)
    for parent,child_set in children.items():
        graph[parent].update(child_set)
    assigned={}
    # Find minimum graph distance from each AI/CS supporting research anchor
    for field, anchors in DOMAINS:
        for anchor in anchors:
            a=anchor.casefold()
            if a not in graph and a not in {n.casefold() for n in names}:continue
            queue=deque([(a,0)])
            visited={a}
            while queue:
                term,d=queue.popleft()
                if d>5:continue
                score=100-13*d
                if term not in assigned or score>assigned[term][0]:
                    assigned[term]=(score,field,anchor,d)
                if d==5:continue
                for nxt in graph[term]:
                    if nxt not in visited:
                        visited.add(nxt);queue.append((nxt,d+1))
    return assigned

def main():
    with INV.open(encoding="utf-8-sig",newline="") as f:
        reader=csv.DictReader(f)
        cols=list(reader.fieldnames or [])
        prior=list(reader)
    assert len(prior)==10100, "Expected 10,100 existing records, got "+str(len(prior))
    batches=Counter(r.get("inventory_batch") for r in prior)
    if batches["003"] or batches["004"]:
        raise RuntimeError("Batch already present; refuse overwrite/duplicate.")
    existing=set()
    for row in prior:existing.update(aliases(row["keyword"]))
    max_id=max(int(r["id"].split("-")[-1]) for r in prior)
    all_names=set();all_labels={};graph=defaultdict(set);version_sources=[]
    for version in VERSIONS:
        try:
            raw,url=download_zip(version)
            names,labels,kids,stats=parse_triples(raw)
            print("Version",version,stats,"topics",len(names),"labels",len(labels),flush=True)
            if len(names)<5000:raise ValueError("Unexpectedly few topics")
            all_names.update(names)
            all_labels.update(labels)
            for p,cs in kids.items():graph[p].update(cs)
            version_sources.append(url)
            if len(all_names)>=23000:break
        except Exception as e:
            print("SOURCE FAILED:",version,repr(e),flush=True)
    if len(all_names)<10000:raise RuntimeError("No sufficient downloadable legitimate CSO topics; no names invented.")
    assigned=classify_and_rank(all_names,graph)
    candidates=[];exclude=Counter()
    for term in all_names:
        name=all_labels.get(term,term).strip()
        if not name or len(name)>115 or len(name)<3 or not re.search(r"[A-Za-z]",name):
            exclude["invalid"]+=1;continue
        if name.lower().startswith(("http://","https://","www.")):
            exclude["url"]+=1;continue
        if aliases(name)&existing:
            exclude["existing_or_alias"]+=1;continue
        # Keep one version across ontology variants
        existing.update(aliases(name))
        score,field,ancestor,d=assigned.get(term.casefold(),(0,"AI-Supporting Computer Science","Computer Science",None))
        # Additional relevance: CSO catalogs publication-driven CS topics. Broad CS
        # entries are admitted only after ranked graph-related research topics.
        candidates.append((score,field,name,ancestor,d,term))
    candidates.sort(key=lambda r:(-r[0],r[1].casefold(),r[2].casefold(),r[5].casefold()))
    if len(candidates)<10000:
        raise RuntimeError(f"Only {len(candidates)} source-backed distinct CSO terms after dedup; need 10000")
    selected=candidates[:10000]
    new=[]
    for i,(score,field,name,ancestor,d,term) in enumerate(selected):
        batch="003" if i<5000 else "004"
        new.append({
            "id":f"AIH-{max_id+i+1:05d}","keyword":name,
            "field":field,"subfield":("CSO: "+ancestor if score>0 else "Computer Science (AI-adjacent candidate)"),
            "first_use_date":"","first_use_evidence":"",
            "research_status":"unverified_first_use",
            "seed_source":SOURCE,
            "historical_reference":"",
            "inventory_batch":batch,
        })
    final=prior+new
    assert len(final)==20100
    assert len({r["id"] for r in final})==20100
    assert len({norm(r["keyword"]) for r in final})==20100
    assert all(not r["first_use_date"] for r in new)
    with INV.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=cols,lineterminator="\n")
        w.writeheader();w.writerows(final)
    report={
        "source":SOURCE,"source_versions":version_sources,
        "source_topics":len(all_names),
        "source_terms_after_existing_dedup":len(candidates),
        "previous_total":len(prior),"added":len(new),"inventory_total":len(final),
        "batch_003":5000,"batch_004":5000,
        "batch_003_ids":[new[0]["id"],new[4999]["id"]],
        "batch_004_ids":[new[5000]["id"],new[-1]["id"]],
        "semantic_classification":{"graph_scored_candidates":sum(r[0]>0 for r in selected),
                                  "supporting_cs_candidates":sum(r[0]==0 for r in selected)},
        "source_exclusions":dict(exclude),
        "all_new_historical_dates_blank":True,
        "categories":dict(sorted(Counter(r["field"] for r in new).items())),
        "license":"Computer Science Ontology: CC BY 4.0",
        "review_note":"Ontology labels and taxonomy relations are sourced; individual AI relevance and earliest use dates are NOT yet human verified."
    }
    OUT.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(report,indent=2,ensure_ascii=False),flush=True)

if __name__=="__main__":main()
