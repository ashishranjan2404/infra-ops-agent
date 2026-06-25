#!/usr/bin/env python3
"""D5 — build SFT (prompt -> completion) data from the SHARED trajectory pool, and
freeze a train/eval scenario split so RFT and SFT consume IDENTICAL data.

SFT target = the highest-reward existing trajectory per train scenario (rejection
sampling / RAFT / STaR-style behavioral cloning of the best demonstration), kept only
if its reward >= --min-reward. RFT will roll out on the SAME train scenarios and be
graded by the SAME grader; both eval on the SAME eval split. That is what makes the
RFT-vs-SFT comparison "same data".

Offline, no network, no HUD import (import-light per 05_ouroboros A1). Python 3.13 ok.

  python3 build_sft_data.py --min-reward 0.5 --seed 7 --train-frac 0.7
"""
from __future__ import annotations

import argparse
import json
import os
import random
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))  # -> /Users/mei/rl
POOL = os.path.join(REPO, "opensre-traj", "out", "hud_trajectories.jsonl")


def _load_pool(path: str) -> list[dict]:
    rows = []
    with open(path) as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def _best_per_scenario(rows: list[dict]) -> dict[str, dict]:
    """argmax reward per scenario, stable tie-break by (reward, model, trace_id)."""
    by_sid: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        sid = r.get("scenario_id")
        if sid:
            by_sid[sid].append(r)
    best = {}
    for sid, rs in by_sid.items():
        best[sid] = max(rs, key=lambda r: (r.get("reward", 0.0),
                                           str(r.get("model", "")),
                                           str(r.get("trace_id", ""))))
    return best


def build(traj_path: str, out_dir: str, min_reward: float, seed: int,
          train_frac: float) -> dict:
    rows = _load_pool(traj_path)
    best = _best_per_scenario(rows)
    scenarios = sorted(best.keys())

    rng = random.Random(seed)
    shuffled = scenarios[:]
    rng.shuffle(shuffled)
    n_train = round(len(shuffled) * train_frac)
    train_ids = sorted(shuffled[:n_train])
    eval_ids = sorted(shuffled[n_train:])

    split = {"seed": seed, "n_scenarios": len(scenarios), "train_frac": train_frac,
             "train": train_ids, "eval": eval_ids}
    with open(os.path.join(out_dir, "split.json"), "w") as fh:
        json.dump(split, fh, indent=2)

    pairs, dropped, teacher_hist = [], [], defaultdict(int)
    for sid in train_ids:
        demo = best[sid]
        if demo.get("reward", 0.0) < min_reward:
            dropped.append(sid)
            continue
        teacher_hist[demo.get("model", "?")] += 1
        pairs.append({
            "scenario_id": sid,
            "prompt_ref": sid,   # full STATIC_PROMPT rendered at train time when HUD env present
            "completion": demo.get("answer", ""),
            "demo_model": demo.get("model"),
            "demo_reward": round(demo.get("reward", 0.0), 4),
            "true_category": demo.get("true_category"),
        })

    sft_path = os.path.join(out_dir, "sft_pairs.jsonl")
    with open(sft_path, "w") as fh:
        for p in pairs:
            fh.write(json.dumps(p) + "\n")

    mean_demo_r = (sum(p["demo_reward"] for p in pairs) / len(pairs)) if pairs else 0.0
    manifest = {
        "n_scenarios": len(scenarios),
        "n_train": len(train_ids),
        "n_eval": len(eval_ids),
        "n_sft_pairs": len(pairs),
        "coverage": round(len(pairs) / len(train_ids), 4) if train_ids else 0.0,
        "min_reward": min_reward,
        "mean_demo_reward": round(mean_demo_r, 4),
        "dropped_no_qualifying_demo": dropped,
        "teacher_model_histogram": dict(teacher_hist),
        "sft_pairs_path": os.path.relpath(sft_path, REPO),
        "split_path": os.path.relpath(os.path.join(out_dir, "split.json"), REPO),
    }
    with open(os.path.join(out_dir, "sft_manifest.json"), "w") as fh:
        json.dump(manifest, fh, indent=2)
    return manifest


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--traj", default=POOL)
    ap.add_argument("--out-dir", default=HERE)
    ap.add_argument("--min-reward", type=float, default=0.5)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--train-frac", type=float, default=0.7)
    args = ap.parse_args()
    m = build(args.traj, args.out_dir, args.min_reward, args.seed, args.train_frac)
    print(json.dumps(m, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
