#!/usr/bin/env python3
"""I6 — Failure-mode taxonomy of REx rollouts.

Buckets every failed / non-clean-win rollout from the project's real rollout data
into interpretable failure modes derived from `rex/scoring.py` signals:

    trap_taken | wrong_root_cause | no_fix | not_resolved | clean_win(excluded)

Two ingest paths:
  A. rex/runs/diagnostic_probe_*.jsonl  — rows already carry score/failed_checks.
  B. rex/runs/hud/*.jsonl               — HUD traces; we REPLAY rex.scoring over the
     captured {plan, scenario, sim_result} request payload (the score response is not
     stored in the trace), using the DETERMINISTIC judge so it is fully hermetic.

Read-only: imports rex.scoring but never mutates any shared file. All outputs land in
this task's artifacts/ dir.

Usage:
    python3 failure_taxonomy.py [--repo /Users/mei/rl] [--out <dir>]
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import sys
from collections import Counter
from dataclasses import dataclass, field, asdict

# --- hermetic deterministic judge (no network) before importing rex.scoring ---
os.environ.setdefault("REX_JUDGE_MODE", "deterministic")

PRIMARY_PRECEDENCE = ["trap_taken", "wrong_root_cause", "no_fix", "not_resolved"]
_CHECK_TO_BUCKET = {
    "trap_action": "trap_taken",
    "root_cause": "wrong_root_cause",
    "correct_fix_missing": "no_fix",
    "not_resolved": "not_resolved",
}


@dataclass
class Rollout:
    source: str
    rollout_id: str
    scenario: str
    score: float
    resolved: bool
    diagnosis_correct: bool
    failed_checks: list = field(default_factory=list)
    n_actions: int = -1     # -1 = unknown (probe rows don't store the plan)
    attempted_trap: bool = False
    primary_bucket: str = ""
    tags: list = field(default_factory=list)
    root_cause_excerpt: str = ""


# ----------------------------------------------------------------------------
def _import_scoring(repo: str):
    if repo not in sys.path:
        sys.path.insert(0, repo)
    import rex.scoring as scoring  # noqa: E402
    return scoring


class _Scenario:
    """Minimal shim exposing only the attributes rex.scoring.score_plan /
    failed_checks read. Built from the flattened scenario fields captured in a
    HUD `rex.score_plan` request payload."""

    def __init__(self, d: dict):
        self.correct_fix_tools = set(d.get("correct_fix_tools", []))
        self.fault_node = d.get("fault_node", "")
        self.trap_actions = d.get("trap_actions", [])
        self.gold_root_description = d.get("gold_root_description", "")
        self.red_herring_hints = d.get("red_herring_hints", [])
        self.category = d.get("category", "unknown")


# ---- Path A: probe jsonl ----------------------------------------------------
def load_probe_rollouts(paths: list, scoring) -> list:
    out = []
    for path in paths:
        for i, line in enumerate(open(path)):
            line = line.strip()
            if not line:
                continue
            d = json.loads(line)
            out.append(Rollout(
                source="probe",
                rollout_id=f"{os.path.basename(path)}:{i}",
                scenario=d.get("scenario", "?"),
                score=float(d.get("score", 0.0)),
                resolved=bool(d.get("resolved", False)),
                diagnosis_correct=bool(d.get("diagnosis_correct", False)),
                failed_checks=list(d.get("failed_checks", [])),
                n_actions=-1,  # unknown: probe rows do not store the action plan
                root_cause_excerpt=(d.get("stated_root_cause", "") or "")[:160],
            ))
    return out


# ---- Path B: HUD traces (replay rex.scoring) --------------------------------
def _payload(span: dict, ev_name: str):
    for e in span.get("events", []):
        if e.get("name") == ev_name:
            return e.get("attributes", {}).get("hud.payload")
    return None


def load_hud_rollouts(paths: list, scoring) -> list:
    seen = set()
    out = []
    for path in paths:
        for line in open(path):
            line = line.strip()
            if not line:
                continue
            span = json.loads(line)
            if span.get("name") != "rex.score_plan":
                continue
            req = _payload(span, "hud.request")
            if not isinstance(req, dict):
                continue
            plan = req.get("plan", {}) or {}
            scen_d = req.get("scenario", {}) or {}
            sim = req.get("sim_result", {}) or {}
            actions = plan.get("actions", []) or []

            # dedup identical episodes across trace files
            key = (scen_d.get("name", "?"), plan.get("root_cause", "")[:80],
                   json.dumps(actions, sort_keys=True))
            if key in seen:
                continue
            seen.add(key)

            scen = _Scenario(scen_d)
            # deterministic + hermetic
            jf = scoring.deterministic_judge
            fc = scoring.failed_checks(plan, scen, sim, judge_fn=jf)
            score, _ = scoring.score_plan(plan, scen, sim, judge_fn=jf)
            diag_ok = scoring.judge_diagnosis(plan.get("root_cause", ""), scen, judge_fn=jf)
            attempted_trap = bool(scoring._traps_in(actions, scen))

            out.append(Rollout(
                source="hud",
                rollout_id=span.get("trace_id", "?")[:12],
                scenario=scen_d.get("name", "?"),
                score=round(float(score), 4),
                resolved=bool(sim.get("resolved", False)),
                diagnosis_correct=diag_ok,
                failed_checks=fc,
                n_actions=len(actions),
                attempted_trap=attempted_trap,
                root_cause_excerpt=(plan.get("root_cause", "") or "")[:160],
            ))
    return out


# ---- bucketing --------------------------------------------------------------
def bucket(r: Rollout):
    fc = set(r.failed_checks)
    if not fc and r.score >= 1.0:
        primary = "clean_win"
    else:
        primary = "not_resolved"  # fallback if some non-mapped check present
        for b in PRIMARY_PRECEDENCE:
            check = next(k for k, v in _CHECK_TO_BUCKET.items() if v == b)
            if check in fc:
                primary = b
                break

    tags = list(r.failed_checks)
    if r.n_actions == 0:  # known-empty plan (HUD); probe rows are -1 (unknown)
        tags.append("empty_plan")
        if "trap_action" not in fc:
            tags.append("safe_abstain")
    if r.attempted_trap and "trap_action" not in fc:
        tags.append("attempted_trap_blocked")
    if r.score == 0.0:
        tags.append("zero_reward")
    return primary, tags


# ---- summary ----------------------------------------------------------------
def summarize(rollouts: list) -> dict:
    for r in rollouts:
        r.primary_bucket, r.tags = bucket(r)
    failed = [r for r in rollouts if r.primary_bucket != "clean_win"]
    n = len(rollouts)

    prim = Counter(r.primary_bucket for r in failed)
    tags = Counter(t for r in failed for t in r.tags)

    by_scn = {}
    for r in rollouts:
        s = by_scn.setdefault(r.scenario, {"n": 0, "failed": 0, "buckets": Counter()})
        s["n"] += 1
        if r.primary_bucket != "clean_win":
            s["failed"] += 1
            s["buckets"][r.primary_bucket] += 1
    for s in by_scn.values():
        s["buckets"] = dict(s["buckets"])

    def pct(c):
        return {k: round(100.0 * v / len(failed), 1) for k, v in c.items()} if failed else {}

    examples = [
        {"rollout_id": r.rollout_id, "source": r.source, "scenario": r.scenario,
         "bucket": r.primary_bucket, "score": r.score, "tags": r.tags,
         "root_cause_excerpt": r.root_cause_excerpt}
        for r in failed[:12]
    ]

    return {
        "corpus": {
            "probe": sum(1 for r in rollouts if r.source == "probe"),
            "hud": sum(1 for r in rollouts if r.source == "hud"),
            "total": n,
        },
        "failure_tail": {
            "n_failed": len(failed),
            "n_clean_win": n - len(failed),
            "n_zero_reward": sum(1 for r in rollouts if r.score == 0.0),
        },
        "primary_bucket_counts": dict(prim),
        "primary_bucket_pct_of_failed": pct(prim),
        "tag_counts": dict(tags),
        "by_scenario": by_scn,
        "caveat": ("Small-N error analysis; counts are over THIS corpus only and do "
                   "not statistically generalize. REx rollouts are single-shot plan "
                   "submissions: there is no wall-clock 'timeout' failure mode; the "
                   "nearest analog is an empty_plan (model abstained / escalated)."),
        "examples": examples,
    }


def render_md(summ: dict) -> str:
    L = ["# I6 — Failure-mode distribution of REx rollouts (real data)", ""]
    c = summ["corpus"]; ft = summ["failure_tail"]
    L += [f"Corpus: **{c['total']}** rollouts (probe={c['probe']}, hud={c['hud']}).",
          f"Failure tail (score<1 OR any failed_check): **{ft['n_failed']} of "
          f"{c['total']}**. Clean wins: {ft['n_clean_win']}. Strict zero-reward: "
          f"{ft['n_zero_reward']}.", "", "## Primary failure bucket (k of failed)"]
    nf = ft["n_failed"]
    for b in PRIMARY_PRECEDENCE:
        k = summ["primary_bucket_counts"].get(b, 0)
        p = summ["primary_bucket_pct_of_failed"].get(b, 0.0)
        L.append(f"- **{b}**: {k} of {nf}  ({p}% of failed)")
    L += ["", "## Secondary tags (k of failed)"]
    for t, k in sorted(summ["tag_counts"].items(), key=lambda x: -x[1]):
        L.append(f"- {t}: {k}")
    L += ["", "## By scenario"]
    for s, d in sorted(summ["by_scenario"].items()):
        L.append(f"- `{s}`: {d['failed']}/{d['n']} failed — {d['buckets']}")
    L += ["", "## Caveat", summ["caveat"], "", "## Example failed rollouts"]
    for e in summ["examples"]:
        L.append(f"- [{e['source']}] `{e['scenario']}` → **{e['bucket']}** "
                 f"(score={e['score']}, tags={e['tags']})")
        L.append(f"    root_cause: {e['root_cause_excerpt']}")
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default="/Users/mei/rl")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    repo = os.path.abspath(args.repo)
    out = args.out or os.path.join(os.path.dirname(os.path.abspath(__file__)))

    scoring = _import_scoring(repo)

    probe_paths = sorted(glob.glob(os.path.join(repo, "rex/runs/diagnostic_probe_*.jsonl")))
    hud_paths = sorted(glob.glob(os.path.join(repo, "rex/runs/hud/*.jsonl")))

    rollouts = load_probe_rollouts(probe_paths, scoring) + load_hud_rollouts(hud_paths, scoring)
    summ = summarize(rollouts)

    with open(os.path.join(out, "failure_report.json"), "w") as f:
        json.dump(summ, f, indent=2)
    with open(os.path.join(out, "failure_report.md"), "w") as f:
        f.write(render_md(summ))

    print(render_md(summ))
    print(f"[wrote] {out}/failure_report.json + failure_report.md")
    return summ


if __name__ == "__main__":
    main()
