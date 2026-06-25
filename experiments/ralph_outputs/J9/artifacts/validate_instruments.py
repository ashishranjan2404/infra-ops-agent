#!/usr/bin/env python3
"""Validate the J9 SRE feedback instruments.

Checks (no external deps, Python 3.13 stdlib):
  1. sre_survey.json and thesis_claims.json parse.
  2. Every quantitative/required survey question that carries a `claim` references a real
     claim id in thesis_claims.json (no dangling claim refs).
  3. No orphan claims: every thesis claim is referenced by >=1 survey question OR an interview
     tag listed in the claim's `tested_by`.
  4. Every question with a `scale` references a scale defined in survey `scales`.
  5. analysis_template.csv header covers the screener + every claim-bearing question id (by
     prefix), so coded data can actually be recorded.

Exit 0 = all green. Exit 1 = at least one failure (printed).
"""
import csv
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def load_json(name):
    return json.loads((HERE / name).read_text())


def main():
    failures = []
    survey = load_json("sre_survey.json")
    claims_doc = load_json("thesis_claims.json")
    claim_ids = {c["id"] for c in claims_doc["claims"]}

    # collect survey questions
    questions = []
    for page in survey["pages"]:
        for q in page["questions"]:
            questions.append(q)

    # Check 2: claim refs valid
    referenced = set()
    for q in questions:
        cid = q.get("claim")
        if cid is None:
            continue
        referenced.add(cid)
        if cid not in claim_ids:
            failures.append(f"[claim-ref] Q {q['id']} references unknown claim '{cid}'")

    # Check 3: no orphan claims (survey OR interview tag in tested_by)
    for c in claims_doc["claims"]:
        tested = set(c.get("tested_by", []))
        survey_hit = c["id"] in referenced
        interview_hit = any(t.startswith("INT_") for t in tested)
        if not (survey_hit or interview_hit):
            failures.append(f"[orphan-claim] claim '{c['id']}' has no survey or interview coverage")

    # Check 4: scales resolve
    scales = set(survey["scales"].keys())
    for q in questions:
        s = q.get("scale")
        if s is not None and s not in scales:
            failures.append(f"[scale] Q {q['id']} uses undefined scale '{s}'")

    # Check 5: CSV header covers screener + claim-bearing questions
    with (HERE / "analysis_template.csv").open() as f:
        header = next(csv.reader(f))
    header_set = set(header)
    need_prefixes = ["respondent_id", "channel", "source"]
    for col in need_prefixes:
        if col not in header_set:
            failures.append(f"[csv] missing meta column '{col}'")
    # every claim-bearing question id should appear as a column or a *_code/*_realism/_flags variant
    for q in questions:
        if q.get("claim") is None:
            continue
        qid = q["id"]
        variants = {qid, f"{qid}_code", f"{qid}_realism", f"{qid}_flags"}
        # matrix/scenario questions are recorded via scenario_* columns
        scenario_cols = {"scenario_A_realism", "scenario_B_realism", "scenario_C_realism",
                         "scenario_unrealistic_flags"}
        if qid.startswith("Q_scenario"):
            if not (scenario_cols & header_set):
                failures.append(f"[csv] no scenario columns to record {qid}")
            continue
        if not (variants & header_set):
            failures.append(f"[csv] no column to record claim-bearing question {qid}")

    # Report
    total_q = len(questions)
    claim_q = sum(1 for q in questions if q.get("claim"))
    print(f"survey questions: {total_q} (claim-bearing: {claim_q})")
    print(f"thesis claims: {len(claim_ids)} | referenced by survey: {len(referenced)}")
    print(f"csv columns: {len(header)}")
    if failures:
        print(f"\nFAIL ({len(failures)} issues):")
        for x in failures:
            print("  -", x)
        return 1
    print("\nOK: all instruments consistent (every claim covered, every item mapped, scales valid, CSV records all items).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
