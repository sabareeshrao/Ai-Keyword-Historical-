#!/usr/bin/env python3
"""Fix an unrelated meaning collision in Reflexion agent framework historical citation."""
import csv,json,re
from pathlib import Path
root=Path(__file__).resolve().parents[1]
db=root/"data/KEYWORD_INVENTORY.csv"
with db.open(encoding="utf-8-sig",newline="") as f:
    reader=csv.DictReader(f);cols=list(reader.fieldnames or []);rows=list(reader)
assert len(rows)==20100
matching=[r for r in rows if r["id"]=="AIH-06007"]
assert len(matching)==1 and matching[0]["keyword"]=="Reflexion"
r=matching[0]
if r["historical_evidence_date"]!="2023":
    assert r["historical_evidence_date"]=="1946",r["historical_evidence_date"]
    assert "10.1038/158422a0" in r["historical_evidence_url"]
r["historical_evidence_date"]="2023"
r["historical_evidence_type"]="primary_method_publication"
r["historical_evidence_title"]="Reflexion: Language Agents with Verbal Reinforcement Learning"
r["historical_evidence_url"]="https://arxiv.org/abs/2303.11366"
r["historical_evidence_authors"]="Noah Shinn; Federico Cassano; Edward Berman; Ashwin Gopinath; Karthik Narasimhan; Shunyu Yao"
r["historical_evidence_notes"]=(
    "Reflexion in the Agentic AI sense denotes the 2023 language-agent "
    "self-reflection framework. Original preprint submitted 20 March 2023; "
    "NeurIPS 2023 publication. Previously matched an unrelated 1946 paper "
    "containing the ordinary English word reflexion. Do not conflate historical "
    "word usage with the named framework's introduction."
)
r["date_status"]="documented_source_not_first_use"
r["display_date"]="2023"
assert not r.get("first_use_date")
with db.open("w",encoding="utf-8",newline="") as f:
    writer=csv.DictWriter(f,fieldnames=cols,lineterminator="\n")
    writer.writeheader();writer.writerows(rows)
report_path=root/"data/DATE_RESEARCH_006_REPORT.json"
report=json.loads(report_path.read_text(encoding="utf-8"))
report["manual_semantic_source_corrections"]=report.get("manual_semantic_source_corrections",0)+1
report["semantic_corrections"]=[{
    "id":"AIH-06007","keyword":"Reflexion",
    "old_year":"1946","old_source":"https://doi.org/10.1038/158422a0",
    "corrected_year":"2023","new_source":"https://arxiv.org/abs/2303.11366",
    "reason":"1946 source used generic English word; 2023 primary source introduced named AI agent framework."
}]
report_path.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
page=root/"batches/date-research-006/page-04.md"
lines=page.read_text(encoding="utf-8").splitlines()
matching_lines=[i for i,line in enumerate(lines) if line.startswith("| AIH-06007 |")]
assert len(matching_lines)==1
lines[matching_lines[0]]="| AIH-06007 | Reflexion | Agentic AI | 2023 | Original agent-framework publication | [Source](https://arxiv.org/abs/2303.11366) |"
page.write_text("\n".join(lines)+"\n",encoding="utf-8")
index=root/"batches/DATE_RESEARCH_006_NEXT_2000.md"
s=index.read_text(encoding="utf-8")
if "## Semantic source correction" not in s:
    s+="\n## Semantic source correction\n\n- **AIH-06007 Reflexion**: rejected a generic 1946 occurrence of the English word. The named language-agent framework was introduced by Shinn and colleagues in the [2023 original paper](https://arxiv.org/abs/2303.11366). This is a documented method-introduction year, not a claim about the English word's first use.\n"
    index.write_text(s,encoding="utf-8")
print("Verified Reflexion agent framework source corrected to 2023, no ID changes.")
