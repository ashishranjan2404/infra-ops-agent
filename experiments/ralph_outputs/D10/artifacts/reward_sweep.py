#!/usr/bin/env python3
"""D10 — Reward-weighting sweep harness (NON-INVASIVE wrapper over rex/scoring.py).

Task: run RFT with different reward weightings — sweep W_ROOT, W_FIX, W_RESOLVED,
TRAP_PENALTY — and show how the composite reward and the RANKING of rollouts change.

We do NOT edit rex/scoring.py. Instead we:
  1. Re-derive the four PRIMITIVE signals scoring.py already computes for a rollout
     (diag_ok, fix_credit, resolved, trap_hit) via its own public helpers
     (judge_diagnosis, _fix_credit, _traps_in) — the deterministic judge, no LLM.
  2. Recombine them under an arbitrary weight vector w = (W_ROOT, W_FIX, W_RESOLVED,
     TRAP_PENALTY), exactly mirroring score_plan's formula:
        score = W_ROOT*diag + W_FIX*fix + W_RESOLVED*resolved  (- TRAP_PENALTY if trap)
        clamped to [0,1].
  3. Generate a REAL rollout bank deterministically (no API): for each scenario we
     enumerate a fixed family of candidate plans (correct fix on target, correct tool
     wrong target, trap action, wrong diagnosis + no fix, empty plan, fix+trap), run
     each through the REAL sim (rex.harness.run_plan), and capture the primitives.
  4. For each weight vector, report composite reward per rollout, the within-scenario
     RANKING, and aggregate ranking-stability metrics (Kendall-tau vs the default
     weights, argmax-flip rate). This is what an RFT reward redesign would change:
     which rollout the policy is pushed toward.

Sanity invariant: at the DEFAULT weights our recomputed composite must EQUAL
score_plan(...) for every rollout (asserted in selftest()).

Run:
    python3 experiments/ralph_outputs/D10/artifacts/reward_sweep.py --selftest
    python3 experiments/ralph_outputs/D10/artifacts/reward_sweep.py \
        --out experiments/ralph_outputs/D10/artifacts/sweep_results.json
"""
from __future__ import annotations

import argparse
import itertools
import json
import os
import sys

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
sys.path.insert(0, REPO)

from rex import scoring  # noqa: E402
from rex.harness import _SCENARIOS, load_scenario, run_plan  # noqa: E402

# Default weights, read straight from the module so we stay in sync with core.
DEFAULT_W = (scoring.W_ROOT, scoring.W_FIX, scoring.W_RESOLVED, scoring.TRAP_PENALTY)

# A focused, defensible sweep grid (not a full cross-product blow-up). Each entry is
# (name, W_ROOT, W_FIX, W_RESOLVED, TRAP_PENALTY). Diagnosis-heavy, fix-heavy,
# resolution-only, zero-trap-penalty, and harsh-trap variants bracket the design space.
SWEEP = [
    ("default",          0.30, 0.25, 0.45, 0.60),
    ("diagnosis_heavy",  0.60, 0.20, 0.20, 0.60),
    ("fix_heavy",        0.20, 0.55, 0.25, 0.60),
    ("resolution_only",  0.00, 0.00, 1.00, 0.60),
    ("equal_thirds",     0.333, 0.333, 0.334, 0.60),
    ("no_trap_penalty",  0.30, 0.25, 0.45, 0.00),
    ("harsh_trap",       0.30, 0.25, 0.45, 1.00),
    ("diag_then_resolve",0.50, 0.05, 0.45, 0.80),
]


# ---- primitive extraction (reuse scoring.py's own helpers; deterministic judge) ----
def primitives(plan: dict, scenario, sim_result: dict) -> dict:
    actions = scoring._applied(plan, sim_result)
    return {
        "diag_ok": bool(scoring.judge_diagnosis(plan.get("root_cause", ""), scenario)),
        "fix": float(scoring._fix_credit(actions, scenario)),
        "resolved": 1.0 if sim_result.get("resolved") else 0.0,
        "trap_hit": bool(scoring._traps_in(actions, scenario)),
    }


def compose(prims: dict, w) -> float:
    W_ROOT, W_FIX, W_RESOLVED, TRAP_PENALTY = w
    s = (W_ROOT * (1.0 if prims["diag_ok"] else 0.0)
         + W_FIX * prims["fix"]
         + W_RESOLVED * prims["resolved"])
    if prims["trap_hit"]:
        s -= TRAP_PENALTY
    return round(max(0.0, min(1.0, s)), 4)


# ---- deterministic rollout bank (REAL sim, no LLM) ---------------------------------
def candidate_plans(scenario):
    """Fixed family of candidate plans per scenario, spanning the reward primitives."""
    fix_tool = sorted(scenario.correct_fix_tools)[0]
    node = scenario.fault_node
    trap = scenario.trap_actions[0] if scenario.trap_actions else None
    good_diag = scenario.gold_root_description
    bad_diag = (scenario.red_herring_hints or ["unknown cause"])[0]

    cands = [
        ("correct_full", {"root_cause": good_diag,
                          "actions": [{"tool": fix_tool, "args": {"target": node}}]}),
        ("fix_wrong_target", {"root_cause": good_diag,
                          "actions": [{"tool": fix_tool, "args": {"target": "__nope__"}}]}),
        ("wrong_diag_no_fix", {"root_cause": bad_diag, "actions": []}),
        ("empty", {"root_cause": "", "actions": []}),
        ("good_diag_no_fix", {"root_cause": good_diag, "actions": []}),
    ]
    if trap:
        cands.append(("trap_only", {"root_cause": bad_diag,
                      "actions": [{"tool": trap["tool"],
                                   "args": {"target": trap.get("target", node)}}]}))
        cands.append(("fix_plus_trap", {"root_cause": good_diag,
                      "actions": [{"tool": fix_tool, "args": {"target": node}},
                                  {"tool": trap["tool"],
                                   "args": {"target": trap.get("target", node)}}]}))
    return cands


def build_rollout_bank(scenario_names):
    bank = []
    for name in scenario_names:
        try:
            sc = load_scenario(name)
        except Exception as e:  # skip any scenario that fails to load
            print(f"  skip {name}: {e}", file=sys.stderr)
            continue
        for label, plan in candidate_plans(sc):
            try:
                sim = run_plan(plan, sc)
            except Exception as e:
                print(f"  skip {name}/{label}: {e}", file=sys.stderr)
                continue
            prims = primitives(plan, sc, sim)
            default_score, _ = scoring.score_plan(plan, sc, sim)
            bank.append({
                "scenario": name, "candidate": label,
                "primitives": prims,
                "score_plan_default": round(default_score, 4),
                "_plan": plan, "_sim_resolved": bool(sim.get("resolved")),
            })
    return bank


# ---- ranking metrics ---------------------------------------------------------------
def kendall_tau(a, b):
    """Kendall tau-b between two score lists (same order). Returns 1.0 for <2 items."""
    n = len(a)
    if n < 2:
        return 1.0
    conc = disc = 0
    for i, j in itertools.combinations(range(n), 2):
        da, db = a[i] - a[j], b[i] - b[j]
        s = da * db
        if s > 0:
            conc += 1
        elif s < 0:
            disc += 1
        # ties contribute to neither (tau-a style numerator); denom uses all pairs
    denom = n * (n - 1) / 2
    return round((conc - disc) / denom, 4) if denom else 1.0


def per_scenario_ranking(bank, w):
    """Group bank by scenario, return {scenario: [(candidate, score) sorted desc]}."""
    by_sc = {}
    for r in bank:
        by_sc.setdefault(r["scenario"], []).append(r)
    out = {}
    for sc, rows in by_sc.items():
        scored = [(row["candidate"], compose(row["primitives"], w)) for row in rows]
        scored.sort(key=lambda x: -x[1])
        out[sc] = scored
    return out


def sweep(bank):
    default_rank = per_scenario_ranking(bank, DEFAULT_W)
    results = []
    for entry in SWEEP:
        wname, *w = entry
        w = tuple(w)
        rank = per_scenario_ranking(bank, w)
        # ranking stability vs default
        taus, argmax_flips, n_sc = [], 0, 0
        for sc in default_rank:
            n_sc += 1
            d_order = [c for c, _ in default_rank[sc]]
            w_scores = dict(rank[sc])
            d_scores = dict(default_rank[sc])
            a = [d_scores[c] for c in d_order]
            b = [w_scores[c] for c in d_order]
            taus.append(kendall_tau(a, b))
            if default_rank[sc][0][0] != rank[sc][0][0]:
                argmax_flips += 1
        mean_tau = round(sum(taus) / len(taus), 4) if taus else 1.0
        # aggregate composite stats over all rollouts
        all_scores = [compose(r["primitives"], w) for r in bank]
        spread = round((max(all_scores) - min(all_scores)), 4) if all_scores else 0.0
        mean_score = round(sum(all_scores) / len(all_scores), 4) if all_scores else 0.0
        results.append({
            "weighting": wname,
            "weights": {"W_ROOT": w[0], "W_FIX": w[1], "W_RESOLVED": w[2],
                        "TRAP_PENALTY": w[3]},
            "mean_composite": mean_score,
            "composite_spread": spread,
            "mean_kendall_tau_vs_default": mean_tau,
            "argmax_flip_rate": round(argmax_flips / n_sc, 4) if n_sc else 0.0,
            "argmax_flips": argmax_flips,
            "n_scenarios": n_sc,
        })
    return results, default_rank


# ---- selftest: recomposed default == score_plan default ----------------------------
def selftest(bank):
    bad = 0
    for r in bank:
        recomposed = compose(r["primitives"], DEFAULT_W)
        if abs(recomposed - r["score_plan_default"]) > 1e-6:
            bad += 1
            print(f"  MISMATCH {r['scenario']}/{r['candidate']}: "
                  f"recomposed={recomposed} score_plan={r['score_plan_default']}")
    assert bad == 0, f"{bad} rollouts disagree with score_plan at default weights"
    print(f"selftest OK: {len(bank)} rollouts, recomposed==score_plan at default weights")
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scenarios", default="", help="comma list; default = a fixed 8-scenario set")
    ap.add_argument("--all", action="store_true", help="use ALL loadable scenarios")
    ap.add_argument("--out", default="")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    if args.all:
        names = sorted(_SCENARIOS)
    elif args.scenarios:
        names = [s.strip() for s in args.scenarios.split(",") if s.strip()]
    else:
        names = ["oom_kill", "cpu_saturation_leaf", "bad_deploy_leaf",
                 "gcp_service_control", "singleton_node_notready",
                 "aws_dynamodb_dns", "cloudflare_waf", "auth_cert_expiry"]

    print(f"building rollout bank over {len(names)} scenarios ...")
    bank = build_rollout_bank(names)
    print(f"  {len(bank)} real rollouts (sim-executed)")

    selftest(bank)
    if args.selftest:
        return

    results, default_rank = sweep(bank)
    out = {
        "default_weights": {"W_ROOT": DEFAULT_W[0], "W_FIX": DEFAULT_W[1],
                            "W_RESOLVED": DEFAULT_W[2], "TRAP_PENALTY": DEFAULT_W[3]},
        "n_scenarios": len(set(r["scenario"] for r in bank)),
        "n_rollouts": len(bank),
        "sweep": results,
        "example_ranking_default": {
            sc: default_rank[sc] for sc in list(default_rank)[:3]
        },
        "rollout_bank": [{k: v for k, v in r.items() if not k.startswith("_")}
                         for r in bank],
    }
    print("\n=== sweep summary ===")
    print(f"{'weighting':<18} {'mean':>6} {'spread':>7} {'tau':>7} {'argmax_flip':>12}")
    for r in results:
        print(f"{r['weighting']:<18} {r['mean_composite']:>6} {r['composite_spread']:>7} "
              f"{r['mean_kendall_tau_vs_default']:>7} {r['argmax_flip_rate']:>12}")

    if args.out:
        os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
        with open(args.out, "w") as f:
            json.dump(out, f, indent=2)
        print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()
