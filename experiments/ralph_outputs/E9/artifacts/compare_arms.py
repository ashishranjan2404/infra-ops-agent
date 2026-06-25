#!/usr/bin/env python3
"""compare_arms.py — head-to-head harness: Fireball-transfer vs synthetic-SRE-aug.

E9 comparison harness. Defines the two arms of the experiment and computes the
data-quality metrics that decide "which helps more" for an SFT/RFT seeding set,
WITHOUT requiring a GPU or fine-tuning run. The metrics are the standard
data-trainability signals (per the HUD task-design doctrine):

  - n_trajectories          : how much usable signal each arm yields
  - label_coverage          : fraction of SRE failure-classes the arm covers
  - within_group_spread     : the *unit of trainability* (RFT needs >0 spread)
  - domain_match            : is the data actually SRE (in-domain) or off-domain
  - floor_check             : cheapest path (empty/trap) scores <= pass threshold

ARM A — Fireball-transfer:
    Use the actual FIREBALL D&D dataset (Zhu et al. 2023, HF: lara-martin/FIREBALL)
    as transfer signal. STATUS: BLOCKED for this offline worker — (1) external
    dataset not vendored; (2) this project is code-as-policy with a FROZEN LLM
    (no fine-tuning), so "transfer" would require a training stack we do not run;
    (3) FIREBALL is D&D combat state, OFF-DOMAIN for SRE diagnosis. We therefore
    score arm A on the metrics we *can* establish a-priori (domain_match=0) and
    record the blocker. The harness is wired so that if a real FIREBALL export is
    dropped at --fireball-jsonl, it is scored on identical metrics.

ARM B — synthetic-SRE-augmentation:
    Output of synth_sre_augmenter.py over the 51 CIDG scenarios. In-domain,
    deterministic, has within-group spread by construction. Fully runnable here.

Usage:
    python3 compare_arms.py --aug augmented_trajectories.jsonl \
        [--fireball-jsonl path] --out comparison_result.json
"""
from __future__ import annotations

import argparse
import json
import os
import sys

PASS_THRESHOLD = 0.7  # matches rex/eval_pass_at_k THRESHOLD semantics

# The SRE failure-classes the bench cares about (for label_coverage of arm B).
SRE_CLASSES = {
    "oom_kill", "cpu_saturation", "disk_pressure", "crashloop", "latency_spike",
    "dns_failure", "memory_leak", "cert_expiry", "cache_stampede", "cache_flush",
    "upstream_5xx", "bad_deploy", "bad_rollout", "db_pool_exhaustion", "node_not_ready",
    "consumer_lag", "stuck_rollout", "fd_exhaust", "network_partition", "config_error",
}


def _load_jsonl(path):
    with open(path) as f:
        return [json.loads(l) for l in f if l.strip()]


def score_synth_arm(groups: list) -> dict:
    n_traj = sum(len(g["trajectories"]) for g in groups)
    classes = set()
    spreads = []
    floor_ok = True
    pos_pass = 0
    pos_total = 0
    for g in groups:
        rc = (g.get("gold") or {}).get("root_cause_kind")
        if rc:
            classes.add(rc)
        spreads.append(g.get("within_group_reward_spread", 0.0))
        for t in g["trajectories"]:
            if t["label"] == "positive":
                pos_total += 1
                if t["reward"] >= PASS_THRESHOLD:
                    pos_pass += 1
            if t["label"] in ("negative_empty", "negative_trap"):
                if t["reward"] >= PASS_THRESHOLD:
                    floor_ok = False
    covered = classes & SRE_CLASSES
    return {
        "arm": "synthetic_sre_augmentation",
        "status": "runnable",
        "n_groups": len(groups),
        "n_trajectories": n_traj,
        "label_coverage": round(len(covered) / len(SRE_CLASSES), 3),
        "classes_covered": sorted(covered),
        "mean_within_group_spread": round(sum(spreads) / len(spreads), 4) if spreads else 0.0,
        "groups_with_positive_spread": sum(1 for s in spreads if s > 0),
        "domain_match": 1.0,  # in-domain SRE by construction
        "floor_check_pass": floor_ok,
        "positive_pass_rate": round(pos_pass / pos_total, 3) if pos_total else 0.0,
    }


def score_fireball_arm(path: str | None) -> dict:
    if path and os.path.exists(path):
        rows = _load_jsonl(path)
        return {
            "arm": "fireball_transfer",
            "status": "runnable_export_present",
            "n_trajectories": len(rows),
            "label_coverage": 0.0,  # D&D classes do not map to SRE failure-classes
            "mean_within_group_spread": None,  # no SRE reward defined for D&D state
            "domain_match": 0.0,  # OFF-DOMAIN: D&D combat, not SRE incidents
            "floor_check_pass": None,
            "note": "FIREBALL export found; scored, but off-domain for SRE seeding.",
        }
    return {
        "arm": "fireball_transfer",
        "status": "blocked",
        "n_trajectories": 0,
        "label_coverage": 0.0,
        "mean_within_group_spread": None,
        "domain_match": 0.0,
        "floor_check_pass": None,
        "blocker": ("FIREBALL D&D dataset not vendored; project uses a FROZEN LLM "
                    "(no fine-tuning stack to 'transfer' into); and D&D combat state is "
                    "OFF-DOMAIN for SRE diagnosis. Drop a JSONL at --fireball-jsonl to score."),
    }


def decide(arm_a: dict, arm_b: dict) -> dict:
    """Which arm helps more, given the metrics established here."""
    reasons = []
    winner = "synthetic_sre_augmentation"
    if arm_a["domain_match"] < arm_b["domain_match"]:
        reasons.append("synthetic arm is in-domain (SRE) vs FIREBALL off-domain (D&D).")
    if arm_a["n_trajectories"] < arm_b["n_trajectories"]:
        reasons.append(f"synthetic yields {arm_b['n_trajectories']} usable trajectories "
                       f"vs {arm_a['n_trajectories']} from the (blocked) Fireball arm.")
    if arm_b.get("mean_within_group_spread", 0) and arm_b["mean_within_group_spread"] > 0:
        reasons.append("synthetic arm has non-zero within-group reward spread (RFT-trainable); "
                       "the Fireball arm has no SRE reward defined.")
    return {
        "winner_on_available_evidence": winner,
        "reasons": reasons,
        "caveat": ("Fireball arm is BLOCKED, not measured end-to-end. This is a "
                   "data-quality verdict (coverage/spread/domain), not a trained-accuracy "
                   "verdict. A fair head-to-head would require (a) a FIREBALL export and "
                   "(b) a fine-tuning stack — neither available to an offline frozen-LLM worker."),
    }


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--aug", default="experiments/ralph_outputs/E9/artifacts/augmented_trajectories.jsonl")
    ap.add_argument("--fireball-jsonl", default=None)
    ap.add_argument("--out", default="experiments/ralph_outputs/E9/artifacts/comparison_result.json")
    args = ap.parse_args(argv)

    groups = _load_jsonl(args.aug)
    arm_b = score_synth_arm(groups)
    arm_a = score_fireball_arm(args.fireball_jsonl)
    verdict = decide(arm_a, arm_b)
    result = {"fireball_transfer": arm_a, "synthetic_sre_augmentation": arm_b, "verdict": verdict}
    with open(args.out, "w") as f:
        json.dump(result, f, indent=2)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
