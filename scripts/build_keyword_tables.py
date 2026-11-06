#!/usr/bin/env python3
import csv
from pathlib import Path
from collections import Counter, defaultdict

ROOT=Path(__file__).resolve().parents[1]
with (ROOT/"data/KEYWORD_INVENTORY.csv").open(encoding="utf-8-sig",newline="") as f:
    rows=list(csv.DictReader(f))
assert len(rows)==20100, len(rows)
assert len({r["id"] for r in rows})==20100
assert len({r["keyword"].casefold() for r in rows})==20100
assert Counter(r.get("inventory_batch") for r in rows)["001"]==5000
assert Counter(r.get("inventory_batch") for r in rows)["002"]==5000
assert Counter(r.get("inventory_batch") for r in rows)["003"]==5000
assert Counter(r.get("inventory_batch") for r in rows)["004"]==5000

def clean(x):
    return str(x or "").replace("|"," / ").replace("\n"," ").strip()

table_dir=ROOT/"tables"
table_dir.mkdir(exist_ok=True)
total=Counter(r["field"] for r in rows if r.get("inventory_batch") in ("001","002","003","004"))
all_index=[
"# Complete AI keyword tables — 20,000 terms",
"",
"Every keyword is included, not a short preview. Four batches of 5,000; each divided into ten GitHub-friendly tables of 500 rows.",
"",
"**Organization:** field A-Z, keyword A-Z. Permanent IDs are unchanged. Historical dates are blank until independently researched.",
"",
"| Batch | Full keyword index | Count |",
"|---|---|---:|",
"| 001 | [Browse 5,000 keywords](../batches/INVENTORY_001_5000.md) | 5,000 |",
"| 002 | [Browse 5,000 keywords](../batches/INVENTORY_002_5000.md) | 5,000 |
| 003 | [Browse 5,000 keywords](../batches/INVENTORY_003_5000.md) | 5,000 |
| 004 | [Browse 5,000 keywords](../batches/INVENTORY_004_5000.md) | 5,000 |",
"| **Total** | **40 tables** | **20,000** |",
"",
"## Category totals","","| Field | Number of keywords |","|---|---:|",
]
all_index += [f"| {clean(k)} | {v} |" for k,v in sorted(total.items(),key=lambda x:x[0].casefold())]
all_index += ["| **Total** | **20,000** |",""]
for number in ["001","002","003","004"]:
    group=sorted([r for r in rows if r.get("inventory_batch")==number],
                 key=lambda x:(x["field"].casefold(),x["keyword"].casefold(),x["id"]))
    assert len(group)==5000
    directory=table_dir/("batch-"+number)
    directory.mkdir(exist_ok=True)
    index=[
        "# Inventory Batch "+number+" — All 5,000 Keywords",
        "",
        "The full 5,000-term inventory is arranged in 10 tables below, each containing 500 rows. No keywords are omitted.",
        "",
        "[Browse all four batches](../tables/README.md) | [Complete master CSV](../data/KEYWORD_INVENTORY.csv)",
        "",
        "## Full keyword tables","","| Page | Keyword count | First term / Last term | Open table |","|---:|---:|---|---|"
    ]
    category_pages=defaultdict(set)
    for offset in range(0,5000,500):
        page=offset//500+1
        block=group[offset:offset+500]
        lines=[
            "# Batch "+number+" — Full keyword table "+str(page).zfill(2)+"/10",
            "",
            "500 keywords; sorted by category then alphabetically. Historical first-use date is pending research.",
            "",
            "[Back to Batch "+number+" index](../../batches/INVENTORY_"+number+"_5000.md)",
            "",
            "| ID | Keyword | Field | Subfield | First-used date |",
            "|---|---|---|---|---|"
        ]
        for r in block:
            date=clean(r.get("first_use_date")) or "—"
            lines.append("| "+ " | ".join([clean(r["id"]),clean(r["keyword"]),clean(r["field"]),clean(r["subfield"]),date])+" |")
            category_pages[r["field"]].add(page)
        lines += ["","— means first-used date has not yet been independently verified.",
                  "", "[Source master file](../../data/KEYWORD_INVENTORY.csv)"]
        (directory/("page-"+str(page).zfill(2)+".md")).write_text("\n".join(lines)+"\n",encoding="utf-8")
        first=clean(block[0]["keyword"])
        last=clean(block[-1]["keyword"])
        index.append("| "+str(page).zfill(2)+" | 500 | "+clean(block[0]["field"])+": "+first+" → "+clean(block[-1]["field"])+": "+last+" | [View all 500](../tables/batch-"+number+"/page-"+str(page).zfill(2)+".md) |")
    index += ["","## Browse by category","","| Field | Number of keywords | Table pages |","|---|---:|---|"]
    counts=Counter(r["field"] for r in group)
    for category in sorted(counts,key=str.casefold):
        page_links=", ".join("[Page "+str(p)+"](../tables/batch-"+number+"/page-"+str(p).zfill(2)+".md)" for p in sorted(category_pages[category]))
        index.append("| "+clean(category)+" | "+str(counts[category])+" | "+page_links+" |")
    index += ["", "**Total: 5,000 real sourced entries.** Date verification and human content review remain pending.",
              "", "Source: https://huggingface.co/datasets/whoashish115/AI-Glossary-Reference (001–002) or https://cso.kmi.open.ac.uk/downloads (003–004; CC BY 4.0)."]
    (ROOT/"batches"/("INVENTORY_"+number+"_5000.md")).write_text("\n".join(index)+"\n",encoding="utf-8")
    all_index += ["## Batch "+number+" — complete tables","",
                  "| Page | Keywords | Link |","|---:|---:|---|"]
    for i in range(1,11):
        all_index.append("| "+str(i).zfill(2)+" | 500 | [Read full table](batch-"+number+"/page-"+str(i).zfill(2)+".md) |")
    all_index.append("")
(table_dir/"README.md").write_text("\n".join(all_index)+"\n",encoding="utf-8")
files=sorted(table_dir.glob("batch-*/page-*.md"))
assert len(files)==40
assert all(sum(line.startswith("| AIH-") for line in f.read_text(encoding="utf-8").splitlines())==500 for f in files)
print("Verified 20 Markdown tables x 500 = 20,000 keyword rows; all IDs preserved.")
