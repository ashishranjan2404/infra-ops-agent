#!/usr/bin/env python3
"""
Verifier = the "rules engine" that turns the binary reward REAL.

For each trajectory it re-checks, from the recorded state_diff + the SLO threshold,
whether the incident actually resolved — instead of trusting the constant label.
This is the infra analog of the D&D rules engine (did the action produce the
correct state change?). Output: action_correct / resolved / guardrail_ok / reward.

Usage:
  python verify.py incidents.jsonl --sample 5000
  python verify.py rejections.jsonl --pathc-rejections
"""
from __future__ import annotations
import argparse, json
from collections import Counter
import generate  # reuse the taxonomy as the source of truth

CORRECT_FIX = {inc["type"]: inc["fix"] for inc in generate.INCIDENTS}
DIRECTION = {inc["type"]: ("lower" if (sum(inc["good"]) / 2) < (sum(inc["bad"]) / 2) else "higher")
             for inc in generate.INCIDENTS}


def verify_trajectory(t: dict) -> dict:
    typ = t["task_type"]
    thr = None
    for s in t["user_input"]["system_state"]:
        if "slo_threshold" in s:
            thr = s["slo_threshold"]
    after = fix_tool = approval = None
    for s in t["trajectory"]:
        if s["role"] == "tool" and isinstance(s.get("content"), dict) and "state_diff" in s["content"]:
            for _, v in s["content"]["state_diff"].items():
                if isinstance(v, dict) and "after" in v:
                    after = v["after"]
            approval = s["content"].get("approval")
            fix_tool = s["name"]
    resolved = False
    if after is not None and thr is not None:
        resolved = (after <= thr) if DIRECTION.get(typ) == "lower" else (after >= thr)
    action_correct = (fix_tool == CORRECT_FIX.get(typ))
    tier = generate.TRUST.get(fix_tool, "autonomous")
    guardrail_ok = (tier == "autonomous") or (approval == "granted_by_human")
    reward = int(resolved and action_correct and guardrail_ok)
    return {"resolved": resolved, "action_correct": action_correct,
            "guardrail_ok": guardrail_ok, "reward": reward, "fix_tool": fix_tool}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    ap.add_argument("--sample", type=int, default=0, help="verify only first N lines")
    ap.add_argument("--pathc-rejections", action="store_true",
                    help="input is rejection samples; report verifier catch-rate by failure_mode")
    args = ap.parse_args()

    n = 0
    agg = Counter()
    by_mode = {}  # failure_mode -> [caught, total]
    with open(args.path) as f:
        for line in f:
            if not line.strip():
                continue
            obj = json.loads(line)
            t = obj["trajectory"] if args.pathc_rejections else obj
            # rejection objects wrap the trajectory under "trajectory"
            traj = obj.get("trajectory") if args.pathc_rejections else obj
            v = verify_trajectory(traj if args.pathc_rejections else obj)
            n += 1
            agg["reward"] += v["reward"]
            agg["resolved"] += v["resolved"]
            agg["action_correct"] += v["action_correct"]
            agg["guardrail_ok"] += v["guardrail_ok"]
            if args.pathc_rejections:
                mode = obj.get("failure_mode", "unknown")
                d = by_mode.setdefault(mode, [0, 0])
                d[1] += 1
                if v["reward"] == 0:        # caught = verifier gives it no reward
                    d[0] += 1
            if args.sample and n >= args.sample:
                break

    print(f"verified {n} trajectories")
    for k in ("reward", "resolved", "action_correct", "guardrail_ok"):
        print(f"  {k:14s}: {agg[k]}/{n}  ({100*agg[k]/n:.1f}%)")
    if args.pathc_rejections:
        print("\nverifier catch-rate by failure_mode (reward==0 = caught):")
        for mode, (caught, tot) in sorted(by_mode.items()):
            print(f"  {mode:26s}: {caught}/{tot}  ({100*caught/tot:.0f}% caught)")


if __name__ == "__main__":
    main()
