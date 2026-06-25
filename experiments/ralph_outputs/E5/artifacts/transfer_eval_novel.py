#!/usr/bin/env python3
"""E5 — Fireball transfer / generalization eval on a NOVEL held-out incident set.

Goal
----
Measure how a candidate policy ("Fireball" — the transfer-target model under test)
GENERALIZES to incidents it has never seen, using the strict zero-overlap held-out
split produced by task A8. The same harness runs any number of baseline policies so
Fireball's transfer number is read against a real reference, not in a vacuum.

This script is self-contained and does NOT modify any shared core file. It only
IMPORTS the frozen core (rex.harness / rex.scoring / rex.loop / agent.llm) and the
A8 manifest, exactly as those modules already support.

Novel set
---------
The 10 incidents are taken from the A8 held-out manifest
(experiments/ralph_outputs/A8/artifacts/heldout_manifest.json), filtered to
`held_out == true`, preferring the `novel` family and then back-filling with the
held-out `simple` incidents until 10 are selected. Every selected key is asserted
to be a loadable rex scenario (present in the generated registry). If A8 is absent,
the script aborts rather than inventing a set.

Policies
--------
A policy is just a name resolved against agent.models.ROSTER plus two synthetic
controls that need no network:
  * ``oracle``  — the gold fix + gold root cause (upper-bound sanity ceiling).
  * ``empty``   — empty plan (lower-bound floor; must score < THRESHOLD).
  * ``fireball``— the transfer target. Resolved from $FIREBALL_MODEL if set, else a
                  roster name passed with --fireball-model. If it cannot be reached
                  it is recorded as BLOCKED (status, error) — never fabricated.
Any roster model name (e.g. glm-5p2, gpt-5.5, claude-haiku-4-5) can be passed as a
baseline; unreachable ones are recorded as blocked, not dropped silently.

Metric
------
Per incident, k seeds of zero-shot transfer (one proposal, deterministic P0 judge),
binary pass at reward >= THRESHOLD. Reports pass@1 with a Wilson 95% CI, mean reward
and within-group std (the unit of trainability), plus a floor/ceiling check.

Usage
-----
    set -a; source ~/.zshrc; set +a
    python3 experiments/ralph_outputs/E5/artifacts/transfer_eval_novel.py \
        --baselines glm-5p2,gpt-5.5 --fireball-model fireball --seeds 3 --n 10
"""
from __future__ import annotations

import argparse
import json
import os
import statistics as st
import sys

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
sys.path.insert(0, REPO)
sys.path.insert(0, os.path.join(REPO, "experiments"))

from compute_pass_at_k import wilson_ci, binary_pass  # noqa: E402
from rex.harness import load_scenario, run_plan, _SCENARIOS  # noqa: E402
from rex.scoring import score_plan  # noqa: E402
from rex.loop import build_prompt, parse_plan  # noqa: E402

THRESHOLD = 0.8
A8_MANIFEST = os.path.join(
    REPO, "experiments", "ralph_outputs", "A8", "artifacts", "heldout_manifest.json"
)


# ---- novel held-out set selection (reuse A8) ------------------------------
def select_novel_set(n: int) -> list:
    """Return up to n A8 held-out incident keys, novel-family first, then simple.
    Each is asserted loadable. Aborts (raises) if A8 is missing — no fabrication."""
    if not os.path.exists(A8_MANIFEST):
        raise FileNotFoundError(
            f"A8 manifest not found at {A8_MANIFEST}; cannot reuse novel set. "
            "Run task A8 first or supply --keys."
        )
    man = json.load(open(A8_MANIFEST))
    held = [e for e in man["per_incident"] if e.get("held_out")]
    fam_rank = {"novel": 0, "cascade": 1, "simple": 2}
    held.sort(key=lambda e: (fam_rank.get(e.get("family"), 9), e["cidg_key"]))
    keys, skipped = [], []
    for e in held:
        k = e["cidg_key"]
        if k not in _SCENARIOS:
            skipped.append(k)
            continue
        keys.append(k)
        if len(keys) >= n:
            break
    if len(keys) < n:
        print(f"  [warn] only {len(keys)} loadable held-out incidents (skipped {skipped})")
    return keys


# ---- policies -------------------------------------------------------------
def make_llm_propose(model: str):
    from agent.llm import call

    def _propose(scenario, seed):
        txt = call(model, build_prompt(scenario, None), max_tokens=1400, temperature=0.7)
        return parse_plan(txt)

    return _propose


def oracle_plan(sc):
    tool = sorted(sc.correct_fix_tools)[0]
    return {"root_cause": sc.gold_root_description,
            "actions": [{"tool": tool, "args": {"target": sc.fault_node}}]}


def empty_plan(_sc):
    return {"root_cause": "", "actions": []}


def score_one(plan, sc):
    sim = run_plan(plan, sc)
    score, _ = score_plan(plan, sc, sim)
    return float(score)


# ---- run one policy across the set ----------------------------------------
def run_policy(name, scenarios, seeds, propose=None, synth=None):
    """Returns {status, per_incident: {key:[rewards]}, error}. synth is a
    deterministic plan(sc) for the no-network controls; propose is the LLM fn."""
    per = {}
    first_err = None
    for key, sc in scenarios.items():
        rewards = []
        for s in range(seeds):
            try:
                plan = synth(sc) if synth else propose(sc, s)
                rewards.append(score_one(plan, sc))
            except Exception as e:  # noqa: BLE001
                first_err = first_err or f"{type(e).__name__}: {str(e)[:120]}"
                break
            if synth:  # deterministic: one seed suffices, replicate
                rewards = rewards * seeds
                break
        per[key] = rewards
    n_done = sum(len(v) for v in per.values())
    status = "ok" if n_done else "blocked"
    return {"status": status, "per_incident": per, "error": first_err}


def summarize(per_incident: dict) -> dict:
    rewards = [r for v in per_incident.values() for r in v]
    n = len(rewards)
    if not n:
        return {"n": 0, "pass@1": None, "ci95": None, "mean_reward": None, "reward_std": None}
    passes = sum(binary_pass(r, THRESHOLD) for r in rewards)
    p1 = passes / n
    lo, hi = wilson_ci(p1, n)
    return {"n": n, "passes": passes, "pass@1": round(p1, 4),
            "ci95": [round(lo, 4), round(hi, 4)],
            "mean_reward": round(st.mean(rewards), 4),
            "reward_std": round(st.pstdev(rewards), 4) if n > 1 else 0.0}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=10, help="number of novel incidents")
    ap.add_argument("--seeds", type=int, default=3)
    ap.add_argument("--baselines", default="glm-5p2",
                    help="comma list of roster model names to run as baselines")
    ap.add_argument("--fireball-model", default=os.environ.get("FIREBALL_MODEL", "fireball"),
                    help="roster name of the Fireball transfer target ($FIREBALL_MODEL)")
    ap.add_argument("--keys", default=None, help="comma list overriding the A8 novel set")
    ap.add_argument("--out", default=os.path.join(os.path.dirname(__file__),
                                                  "..", "transfer_results.json"))
    args = ap.parse_args()

    keys = (args.keys.split(",") if args.keys else select_novel_set(args.n))
    scenarios = {k: load_scenario(k) for k in keys}
    print(f"novel set ({len(keys)}): {keys}\n")

    report = {"threshold": THRESHOLD, "seeds": args.seeds, "n_incidents": len(keys),
              "novel_set": keys, "source": "A8 heldout_manifest.json (held_out==true)",
              "policies": {}}

    # synthetic controls
    for cname, fn in (("empty", empty_plan), ("oracle", oracle_plan)):
        r = run_policy(cname, scenarios, args.seeds, synth=fn)
        report["policies"][cname] = {"kind": "control", **r, "summary": summarize(r["per_incident"])}

    # baselines + fireball target
    targets = [(b.strip(), "baseline") for b in args.baselines.split(",") if b.strip()]
    targets.append((args.fireball_model, "fireball"))
    for model, kind in targets:
        try:
            propose = make_llm_propose(model)
        except KeyError as e:
            report["policies"][model] = {"kind": kind, "status": "blocked",
                                         "error": f"not in ROSTER: {e}", "per_incident": {},
                                         "summary": summarize({})}
            print(f"  {model} ({kind}): BLOCKED — not in roster")
            continue
        r = run_policy(model, scenarios, args.seeds, propose=propose)
        report["policies"][model] = {"kind": kind, **r, "summary": summarize(r["per_incident"])}
        s = report["policies"][model]["summary"]
        tag = "BLOCKED" if r["status"] == "blocked" else f"pass@1={s['pass@1']} mean={s['mean_reward']}"
        print(f"  {model} ({kind}): {tag}" + (f"  [{r['error']}]" if r["error"] else ""))

    # floor / ceiling check
    fc = report["policies"]["empty"]["summary"]
    cc = report["policies"]["oracle"]["summary"]
    report["floor_ceiling"] = {
        "empty_mean": fc["mean_reward"], "oracle_mean": cc["mean_reward"],
        "floor_ok": (fc["pass@1"] == 0.0) if fc["pass@1"] is not None else None,
        "ceiling_ok": (cc["pass@1"] == 1.0) if cc["pass@1"] is not None else None,
    }

    out = os.path.abspath(args.out)
    json.dump(report, open(out, "w"), indent=2)
    print(f"\nfloor/ceiling: {report['floor_ceiling']}")
    print(f"-> {out}")
    return report


if __name__ == "__main__":
    main()
