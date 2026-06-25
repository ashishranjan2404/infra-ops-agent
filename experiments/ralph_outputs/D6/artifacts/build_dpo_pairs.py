"""D6 — DPO preference-pair constructor from override/reward data.

We treat the per-trajectory HUD reward (deterministic SRE judge in rex/scoring.py)
as a *preference signal*. For every incident scenario that has >=2 trajectories with
distinct rewards, the higher-reward answer is the human-preferred ("override toward")
completion and a lower-reward answer is the rejected one. This is exactly the
preference data a human-override / escalate-review loop would emit:
"the on-call accepted diagnosis A and rejected diagnosis B for the same incident".

Output: DPO triples {prompt, chosen, rejected, metadata} ready for a DPO trainer
(TRL DPOTrainer / HUD Tinker preference API). No training is run here — see
dpo_config.yaml + the documented backend blocker.

Pure-stdlib, no third-party deps, so the unit test runs anywhere.
"""
from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass, asdict
from itertools import combinations
from typing import Iterable

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
DEFAULT_TRAJ = os.path.join(REPO_ROOT, "opensre-traj", "out", "hud_trajectories.jsonl")
DEFAULT_SPECS = os.path.join(REPO_ROOT, "opensre-traj", "specs")


@dataclass(frozen=True)
class DPOExample:
    prompt: str
    chosen: str
    rejected: str
    chosen_reward: float
    rejected_reward: float
    margin: float
    scenario_id: str
    incident: str
    chosen_model: str
    rejected_model: str


def load_trajectories(path: str) -> list[dict]:
    rows = []
    with open(path) as fh:
        for ln in fh:
            ln = ln.strip()
            if ln:
                rows.append(json.loads(ln))
    return rows


def build_prompt(incident: str, specs_dir: str = DEFAULT_SPECS) -> str:
    """Reconstruct the incident prompt from its scenario spec.

    Falls back to a minimal prompt if the spec file is missing so pair
    construction never silently drops a scenario.
    """
    spec_path = os.path.join(specs_dir, f"{incident}.json")
    if not os.path.exists(spec_path):
        return f"You are an SRE. Diagnose and remediate the incident: {incident}."
    spec = json.load(open(spec_path))
    alert = spec.get("alert", {})
    title = alert.get("title", incident)
    summary = (alert.get("commonAnnotations", {}) or {}).get("summary", "")
    return (
        "You are an on-call SRE. An alert has fired. Investigate using read-only "
        "tools, then give a root-cause diagnosis, the evidence, the ruled-out "
        "red herrings, and a single safe remediation.\n"
        f"ALERT: {title}\n"
        f"SUMMARY: {summary}"
    ).strip()


def construct_pairs(
    rows: Iterable[dict],
    *,
    min_margin: float = 0.10,
    max_pairs_per_scenario: int | None = None,
    specs_dir: str = DEFAULT_SPECS,
) -> list[DPOExample]:
    """Group trajectories by scenario; emit (chosen, rejected) where the reward
    margin >= min_margin. Degenerate answers (empty) are skipped. Deterministic
    ordering (sorted by scenario, then descending margin)."""
    by_scn: dict[str, list[dict]] = {}
    for r in rows:
        if not (r.get("answer") or "").strip():
            continue
        by_scn.setdefault(r["scenario_id"], []).append(r)

    out: list[DPOExample] = []
    for scn in sorted(by_scn):
        traj = by_scn[scn]
        incident = traj[0].get("incident", scn)
        prompt = build_prompt(incident, specs_dir)
        pairs: list[DPOExample] = []
        for a, b in combinations(traj, 2):
            hi, lo = (a, b) if a["reward"] >= b["reward"] else (b, a)
            margin = round(hi["reward"] - lo["reward"], 6)
            if margin < min_margin:
                continue
            # guard against identical text (e.g. same model twice)
            if hi["answer"].strip() == lo["answer"].strip():
                continue
            pairs.append(
                DPOExample(
                    prompt=prompt,
                    chosen=hi["answer"],
                    rejected=lo["answer"],
                    chosen_reward=round(hi["reward"], 6),
                    rejected_reward=round(lo["reward"], 6),
                    margin=margin,
                    scenario_id=scn,
                    incident=incident,
                    chosen_model=hi.get("model", "?"),
                    rejected_model=lo.get("model", "?"),
                )
            )
        pairs.sort(key=lambda e: -e.margin)
        if max_pairs_per_scenario is not None:
            pairs = pairs[:max_pairs_per_scenario]
        out.extend(pairs)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--traj", default=DEFAULT_TRAJ)
    ap.add_argument("--specs", default=DEFAULT_SPECS)
    ap.add_argument("--out", default=os.path.join(os.path.dirname(__file__), "dpo_pairs.jsonl"))
    ap.add_argument("--min-margin", type=float, default=0.10)
    ap.add_argument("--max-per-scenario", type=int, default=4)
    args = ap.parse_args()

    rows = load_trajectories(args.traj)
    pairs = construct_pairs(
        rows,
        min_margin=args.min_margin,
        max_pairs_per_scenario=args.max_per_scenario,
        specs_dir=args.specs,
    )
    with open(args.out, "w") as fh:
        for ex in pairs:
            fh.write(json.dumps(asdict(ex)) + "\n")
    scenarios = len({e.scenario_id for e in pairs})
    print(f"trajectories={len(rows)} pairs={len(pairs)} scenarios={scenarios} -> {args.out}")
    if pairs:
        avg = sum(e.margin for e in pairs) / len(pairs)
        print(f"avg_margin={avg:.3f} max_margin={max(e.margin for e in pairs):.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
