"""Build a human-relabeling worksheet + compute the machine-vs-machine IAA baseline.

Task B13. Produces two real artifacts from the repo's actual scenarios + judge:

  1. relabel_worksheet.csv   — one row per (scenario, candidate stated_cause). Columns:
       episode_id, scenario, gold_root, red_herrings, stated_cause,
       machine_label (CORRECT/WRONG from deterministic_judge), human_label (BLANK),
       notes (BLANK)
     Humans fill `human_label` with CORRECT or WRONG, blind to `machine_label`
     (the protocol in 04_spec.md says to ship a blinded copy with that column hidden).

  2. machine_baseline.json   — machine-vs-machine agreement. Because the judge is a
     deterministic function, re-running it must reproduce identical labels: Cohen's
     kappa == 1.0. We ALSO run a perturbed "judge2" (the continuous mechanism_score
     thresholded at 0.5) to show kappa between two DIFFERENT deterministic graders,
     which is the honest, non-trivial machine baseline.

Candidates per scenario: we synthesise a small, deterministic panel of stated-causes
(no LLM, no network) so the worksheet is reproducible:
   - the gold description           -> expected CORRECT
   - the first red herring          -> expected WRONG
   - a generic non-answer           -> expected WRONG
This is enough to exercise both judge labels and give humans real disagreement to rule
on (paraphrase of gold, borderline herrings).

Usage:
    python3 build_worksheet.py                 # writes both artifacts next to this file
"""
from __future__ import annotations

import csv
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, REPO)
sys.path.insert(0, os.path.join(REPO, "experiments"))

from rex.harness import _SCENARIOS, load_scenario  # noqa: E402
from rex.scoring import deterministic_judge, mechanism_score  # noqa: E402

from iaa import cohen_kappa, percent_agreement  # noqa: E402


def _candidates(sc) -> list[tuple[str, str]]:
    """(stated_cause, provenance) panel for one scenario. Deterministic, no LLM."""
    cands = [(sc.gold_root_description, "gold")]
    if sc.red_herring_hints:
        cands.append((f"the incident is caused by {sc.red_herring_hints[0]}", "herring"))
    cands.append(("the service is just overloaded and needs more replicas", "generic"))
    return cands


def build_rows(scenario_names: list[str]) -> list[dict]:
    rows = []
    for name in scenario_names:
        sc = load_scenario(name)
        for j, (cause, prov) in enumerate(_candidates(sc)):
            m = deterministic_judge(cause, sc.gold_root_description, sc.red_herring_hints)
            rows.append({
                "episode_id": f"{name}#{j}",
                "scenario": name,
                "provenance": prov,
                "gold_root": sc.gold_root_description,
                "red_herrings": " | ".join(sc.red_herring_hints),
                "stated_cause": cause,
                "machine_label": "CORRECT" if m else "WRONG",
                "human_label": "",      # humans fill this in (blinded copy hides machine_label)
                "notes": "",
            })
    return rows


def write_worksheet(rows: list[dict], path: str) -> None:
    cols = ["episode_id", "scenario", "provenance", "gold_root", "red_herrings",
            "stated_cause", "machine_label", "human_label", "notes"]
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)


def machine_baseline(rows: list[dict]) -> dict:
    """Two deterministic graders over the SAME episodes:
       judge1 = deterministic_judge (already in machine_label)
       judge2 = mechanism_score >= 0.5  (a DIFFERENT continuous grader, thresholded)
    Report Cohen's kappa + percent agreement for (judge1 vs judge1) and (judge1 vs judge2).
    """
    a, b = [], []   # judge1, judge2 labels as bool->CORRECT/WRONG
    for r in rows:
        sc = load_scenario(r["scenario"])
        cause = r["stated_cause"]
        j1 = deterministic_judge(cause, sc.gold_root_description, sc.red_herring_hints)
        j2 = mechanism_score(cause, sc.gold_root_description, sc.red_herring_hints) >= 0.5
        a.append("CORRECT" if j1 else "WRONG")
        b.append("CORRECT" if j2 else "WRONG")

    return {
        "n_episodes": len(rows),
        "judge1_vs_judge1": {
            "description": "deterministic_judge re-run on identical inputs (idempotence check)",
            "cohen_kappa": cohen_kappa(a, a),
            "percent_agreement": percent_agreement(a, a),
        },
        "judge1_vs_judge2": {
            "description": "deterministic_judge vs mechanism_score>=0.5 (two different graders)",
            "cohen_kappa": round(cohen_kappa(a, b), 4),
            "percent_agreement": round(percent_agreement(a, b), 4),
        },
        "label_distribution_judge1": {
            "CORRECT": a.count("CORRECT"), "WRONG": a.count("WRONG")},
        "label_distribution_judge2": {
            "CORRECT": b.count("CORRECT"), "WRONG": b.count("WRONG")},
    }


def main() -> int:
    names = sorted(_SCENARIOS)
    rows = build_rows(names)
    ws_path = os.path.join(HERE, "relabel_worksheet.csv")
    bl_path = os.path.join(HERE, "machine_baseline.json")
    write_worksheet(rows, ws_path)
    baseline = machine_baseline(rows)
    with open(bl_path, "w") as f:
        json.dump(baseline, f, indent=2)
    print(f"wrote {ws_path}  ({len(rows)} episodes across {len(names)} scenarios)")
    print(f"wrote {bl_path}")
    print(json.dumps(baseline, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
