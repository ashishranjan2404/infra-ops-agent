#!/usr/bin/env python3
"""D5 — RFT vs SFT comparison harness on IDENTICAL data.

Two modes:

  --offline   No network, no HUD. Computes a PROXY CEILING: grades the best existing
              demo per EVAL-split scenario with the v2 grader weights, plus a keyword-
              stuffing hack diagnostic. This is an UPPER BOUND on what cloning these
              demos could achieve on held-out scenarios — it is NOT a trained SFT/RFT
              result. Labeled `proxy_ceiling` throughout (05_ouroboros B2).

  post-training (--rft-log / --sft-log)   Reads each leg's run log, reports final mean
              held-out reward, delta vs base, per-subscore breakdown, hack diagnostic,
              and declares a winner. Blank until the GPU/Tinker legs run.

  python3 compare_harness.py --offline
  python3 compare_harness.py --rft-log runs/rft.jsonl --sft-log runs/sft.jsonl --base 0.50
"""
from __future__ import annotations

import argparse
import json
import os
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
POOL = os.path.join(REPO, "opensre-traj", "out", "hud_trajectories.jsonl")

import sys
sys.path.insert(0, REPO)
from rex.scoring import mechanism_score  # deterministic, import-light (no HUD)

# v2 grader weights (mirror hud_env_v2._grade_v2)
W = {"root_cause_category": 0.35, "mechanism_match": 0.20,
     "evidence_keywords": 0.25, "ruled_out_red_herrings": 0.10, "remediation_tool": 0.10}


def _load(path):
    with open(path) as fh:
        return [json.loads(l) for l in fh if l.strip()]


def _best_per_scenario(rows):
    by = defaultdict(list)
    for r in rows:
        by[r["scenario_id"]].append(r)
    return {s: max(rs, key=lambda r: (r.get("reward", 0.0), str(r.get("model")),
                                      str(r.get("trace_id")))) for s, rs in by.items()}


def _v2_reward_from_subscores(row):
    """Recombine the four stored subscores with v2 weights + a recomputed mechanism term.
    Pool subscores are pre-v2 (no mechanism_match); we recompute mechanism from the answer
    against true_category as a coarse gold, red-herrings unknown offline -> [] (documented)."""
    ss = dict(row.get("subscores", {}))
    ans = row.get("answer", "") or ""
    gold = row.get("true_category", "") or ""
    ss["mechanism_match"] = mechanism_score(ans, gold.replace("_", " "), [])
    return round(sum(W[k] * ss.get(k, 0.0) for k in W), 4), ss


def _hack_diag(row):
    ans = (row.get("answer", "") or "")
    per100 = max(len(ans) / 100.0, 1e-9)
    ss = row.get("subscores", {})
    # density proxies from stored subscores (fraction of kw present, normalized by length)
    req = ss.get("evidence_keywords", 0.0)
    herr = ss.get("ruled_out_red_herrings", 0.0)
    return {"answer_chars": len(ans),
            "req_kw_score": round(req, 3),
            "herring_kw_score": round(herr, 3),
            "req_density_per100c": round(req / per100, 4)}


def offline(split_path, traj_path):
    split = json.load(open(split_path))
    rows = _load(traj_path)
    best = _best_per_scenario(rows)
    eval_ids = [s for s in split["eval"] if s in best]
    skipped = [s for s in split["eval"] if s not in best]

    table, agg = [], defaultdict(float)
    for sid in eval_ids:
        row = best[sid]
        rew, ss = _v2_reward_from_subscores(row)
        diag = _hack_diag(row)
        table.append({"scenario_id": sid, "teacher": row.get("model"),
                      "proxy_ceiling_v2": rew, "subscores": {k: round(ss.get(k, 0.0), 3) for k in W},
                      "hack": diag})
        for k in W:
            agg[k] += ss.get(k, 0.0)
        agg["proxy_ceiling_v2"] += rew

    n = len(eval_ids) or 1
    summary = {"mode": "offline_proxy_ceiling",
               "caption": "UPPER BOUND on cloning best demos on held-out scenarios; "
                          "NOT a trained SFT/RFT result.",
               "n_eval_scenarios_graded": len(eval_ids), "skipped_no_demo": skipped,
               "mean_proxy_ceiling_v2": round(agg["proxy_ceiling_v2"] / n, 4),
               "mean_subscores": {k: round(agg[k] / n, 4) for k in W}}
    out = {"summary": summary, "per_scenario": table}
    with open(os.path.join(HERE, "comparison.json"), "w") as fh:
        json.dump(out, fh, indent=2)

    print("=== D5 OFFLINE PROXY CEILING (held-out eval split) ===")
    print(summary["caption"])
    print(f"graded {len(eval_ids)} eval scenarios; skipped (no demo): {skipped}")
    print(f"mean proxy_ceiling_v2 = {summary['mean_proxy_ceiling_v2']}")
    print("mean subscores:", json.dumps(summary["mean_subscores"]))
    print(f"\n{'scenario':32}{'teacher':18}{'proxy_v2':>9}{'mechan':>8}{'chars':>7}")
    for r in table:
        print(f"{r['scenario_id']:32}{str(r['teacher']):18}{r['proxy_ceiling_v2']:>9.3f}"
              f"{r['subscores']['mechanism_match']:>8.2f}{r['hack']['answer_chars']:>7}")
    print("\nwrote comparison.json")
    return 0


def post_training(rft_log, sft_log, base):
    def final_mean(path):
        if not path or not os.path.exists(path):
            return None
        rows = _load(path)
        rews = [r.get("mean_reward") for r in rows if r.get("mean_reward") is not None]
        return round(rews[-1], 4) if rews else None
    rft = final_mean(rft_log)
    sft = final_mean(sft_log)
    res = {"mode": "post_training", "base_mean_reward": base,
           "rft_final": rft, "sft_final": sft,
           "rft_gain": (round(rft - base, 4) if rft is not None and base is not None else None),
           "sft_gain": (round(sft - base, 4) if sft is not None and base is not None else None)}
    if res["rft_gain"] is not None and res["sft_gain"] is not None:
        res["winner"] = "RFT" if res["rft_gain"] > res["sft_gain"] else "SFT"
    else:
        res["winner"] = "PENDING (one or both legs not yet run — see blocker)"
    with open(os.path.join(HERE, "comparison.json"), "w") as fh:
        json.dump(res, fh, indent=2)
    print(json.dumps(res, indent=2))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--offline", action="store_true")
    ap.add_argument("--split", default=os.path.join(HERE, "split.json"))
    ap.add_argument("--traj", default=POOL)
    ap.add_argument("--rft-log", default="")
    ap.add_argument("--sft-log", default="")
    ap.add_argument("--base", type=float, default=None)
    args = ap.parse_args()
    if args.offline or not (args.rft_log or args.sft_log):
        return offline(args.split, args.traj)
    return post_training(args.rft_log, args.sft_log, args.base)


if __name__ == "__main__":
    raise SystemExit(main())
