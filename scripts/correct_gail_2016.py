#!/usr/bin/env python3
"""Correct a verified acronym collision in 2000-keyword date research."""
import csv,json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
path=root/"data/KEYWORD_INVENTORY.csv"
with path.open(encoding="utf-8",newline="") as f:
    reader=csv.DictReader(f)
    fields=list(reader.fieldnames or [])
    rows=list(reader)
assert len(rows)==20100
selected=[r for r in rows if r["id"]=="AIH-02503"]
assert len(selected)==1 and selected[0]["keyword"]=="GAIL"
r=selected[0]
oldsource=r.get("historical_evidence_url")
oldyear=r.get("historical_evidence_date")
assert oldsource in (
    "https://doi.org/10.1016/s0140-6736(05)74761-9",
    "https://doi.org/10.1016/S0140-6736(05)74761-9",
    "https://arxiv.org/abs/1606.03476",
),f"Unexpected current GAIL source {oldsource}"
r["historical_evidence_date"]="2016"
r["historical_evidence_type"]="primary_method_publication"
r["historical_evidence_title"]="Generative Adversarial Imitation Learning"
r["historical_evidence_url"]="https://arxiv.org/abs/1606.03476"
r["historical_evidence_authors"]="Jonathan Ho; Stefano Ermon"
r["historical_evidence_notes"]=(
    "AI sense: generative adversarial imitation learning (GAIL), first arXiv preprint 2016-06-10. "
    "Unrelated 2000 Lancet Gail breast-cancer paper rejected as cross-domain surname collision. "
    "Documented introduction, NOT independently proven first-ever use of every possible acronym sense."
)
r["date_status"]="documented_source_not_first_use"
r["display_date"]="2016"
assert not r.get("first_use_date")
with path.open("w",encoding="utf-8",newline="") as f:
    writer=csv.DictWriter(f,fieldnames=fields,lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
report_path=root/"data/DATE_RESEARCH_005_REPORT.json"
report=json.loads(report_path.read_text())
report["manual_semantic_source_corrections"]=1
report["source_correction_details"]={
    "keyword_id":"AIH-02503",
    "keyword":"GAIL",
    "rejected_source":"https://doi.org/10.1016/s0140-6736(05)74761-9",
    "accepted_source":"https://arxiv.org/abs/1606.03476",
    "corrected_publication_year":"2016",
    "reason":"Exclude unrelated use of surname Gail in Lancet cancer research."
}
report_path.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
index_path=root/"batches/DATE_RESEARCH_005_NEXT_2000.md"
index=index_path.read_text()
if "## Source correction" not in index:
    index+="\n## Source correction\n\nAIH-02503 (GAIL): rejected an unrelated 2000 cancer-research surname match and linked the original 2016 Generative Adversarial Imitation Learning paper by Ho and Ermon. Its year remains a dated original method publication, not a claim about every earlier use of the acronym.\n"
    index_path.write_text(index,encoding="utf-8")
print("GAIL source corrected to primary 2016 AI method publication; fixed IDs preserved.")
