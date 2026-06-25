#!/usr/bin/env python3
"""D9 — Curriculum-scheduled training config builder.

Consumes the A12 difficulty ordering (experiments/ralph_outputs/A12/artifacts/
curriculum_order.json) and emits a concrete, deterministic *training schedule*:
an ordered list of (epoch, stage, incident_ids, sampling_weights) that a
downstream RFT/GRPO loop (e.g. opensre-traj/train_rft_v2.py or the HUD Tinker
SDK) can iterate without re-deriving difficulty.

The schedule supports three orderings so the comparison harness can A/B them:
  - "curriculum"  : easy -> hard, banded into stages (the A12 order).
  - "random"      : deterministic shuffle (seeded), no difficulty structure.
  - "anti"        : hard -> easy (control: curriculum reversed).

Banding: the N incidents are split into `n_stages` contiguous difficulty bands.
A curriculum run "unlocks" bands progressively (stage k trains on bands 0..k),
with a configurable rehearsal weight so earlier (easier) bands keep being
sampled (mitigates catastrophic forgetting). Random/anti runs see the SAME
total sample budget but with the band structure flattened / reversed.

This file ONLY builds the schedule + config (pure, deterministic, no model
calls). The actual gradient training is a documented blocker (no GPU / frozen
LLM in this environment) — see the comparison harness for the eval-side proxy.

Usage:
    python3 curriculum_schedule.py --print
    python3 curriculum_schedule.py --order curriculum --stages 5 --out sched.json
"""
from __future__ import annotations

import argparse
import json
import os
import random

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
A12 = os.path.join(REPO, "experiments", "ralph_outputs", "A12", "artifacts",
                   "curriculum_order.json")
DEFAULT_OUT = os.path.join(HERE, "training_config.json")


def load_order() -> dict:
    """Load A12 ordering. Hard-required input; fail loudly if missing."""
    if not os.path.exists(A12):
        raise FileNotFoundError(
            f"A12 curriculum_order.json not found at {A12}; run A12/build_curriculum.py first")
    with open(A12) as f:
        return json.load(f)


def _bands(ids: list, n_stages: int) -> list:
    """Split an ordered id list into n_stages contiguous bands (near-equal)."""
    n = len(ids)
    n_stages = max(1, min(n_stages, n))
    base, extra = divmod(n, n_stages)
    bands, i = [], 0
    for s in range(n_stages):
        size = base + (1 if s < extra else 0)
        bands.append(ids[i:i + size])
        i += size
    return bands


def build_schedule(order: str = "curriculum", n_stages: int = 5,
                   rehearsal: float = 0.3, seed: int = 1234,
                   samples_per_incident: int = 8) -> dict:
    """Return a deterministic training schedule dict.

    rehearsal: weight (0..1) given to PREVIOUSLY-unlocked bands relative to the
               newly-unlocked band (which always has weight 1.0). 0 => no
               rehearsal (pure progressive); 1 => uniform over unlocked bands.
    """
    data = load_order()
    easy_to_hard = list(data["order_easy_to_hard"])
    diff = {r["id"]: r["difficulty"] for r in data["incidents"]}

    if order == "curriculum":
        ordered = easy_to_hard
    elif order == "anti":
        ordered = list(reversed(easy_to_hard))
    elif order == "random":
        ordered = list(easy_to_hard)
        random.Random(seed).shuffle(ordered)
    else:
        raise ValueError(f"unknown order: {order!r} (curriculum|random|anti)")

    bands = _bands(ordered, n_stages)

    stages = []
    for k in range(len(bands)):
        if order == "curriculum":
            # progressive unlock + rehearsal of earlier bands
            active = []
            for j in range(k + 1):
                w = 1.0 if j == k else rehearsal
                for inc in bands[j]:
                    active.append({"id": inc, "weight": round(w, 4),
                                   "difficulty": diff.get(inc)})
        else:
            # random / anti: every stage sees its own band only, uniform weight
            # (no difficulty-aware unlocking — this is the control structure).
            active = [{"id": inc, "weight": 1.0, "difficulty": diff.get(inc)}
                      for inc in bands[k]]
        total_samples = sum(round(a["weight"] * samples_per_incident)
                            for a in active)
        stages.append({
            "stage": k,
            "epoch": k,
            "newly_unlocked": bands[k],
            "active_incidents": active,
            "n_active": len(active),
            "samples_this_stage": total_samples,
        })

    total_budget = sum(s["samples_this_stage"] for s in stages)
    return {
        "order": order,
        "n_stages": len(bands),
        "rehearsal": rehearsal,
        "seed": seed,
        "samples_per_incident": samples_per_incident,
        "source_signal": data.get("signal"),
        "n_incidents": len(ordered),
        "total_sample_budget": total_budget,
        "ordered_ids": ordered,
        "stages": stages,
    }


def training_config(n_stages: int = 5, rehearsal: float = 0.3,
                    seed: int = 1234) -> dict:
    """Full RFT/GRPO-style config object embedding the curriculum schedule.

    Field names mirror the opensre RFT runner so this can be dropped in once a
    GPU/training backend is available.
    """
    sched = build_schedule("curriculum", n_stages, rehearsal, seed)
    return {
        "experiment": "D9-curriculum-rft",
        "base_model": "Qwen3-8B (forked slug, see rft-training-run memory)",
        "algorithm": "GRPO",
        "reward": "rex.scoring.score_plan (deterministic root-cause judge)",
        "group_size": 8,
        "lr": 1e-6,
        "kl_coeff": 0.02,
        "max_tokens": 4000,
        "epochs_per_stage": 1,
        "advance_criterion": {
            "metric": "mean_stage_reward",
            "threshold": 0.55,
            "patience_epochs": 2,
            "note": "advance to next band when running mean reward on the "
                    "current band clears threshold OR patience exhausted",
        },
        "curriculum": sched,
        "blocker": "No GPU / training backend in this env (frozen-LLM project). "
                   "Config + schedule are runnable inputs; gradient step is "
                   "out of scope here — see comparison harness for eval proxy.",
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--order", default="curriculum",
                    choices=["curriculum", "random", "anti"])
    ap.add_argument("--stages", type=int, default=5)
    ap.add_argument("--rehearsal", type=float, default=0.3)
    ap.add_argument("--seed", type=int, default=1234)
    ap.add_argument("--out", default=DEFAULT_OUT)
    ap.add_argument("--print", action="store_true", dest="show")
    args = ap.parse_args()

    cfg = training_config(args.stages, args.rehearsal, args.seed)
    with open(args.out, "w") as f:
        json.dump(cfg, f, indent=2)
    print(f"wrote {args.out}  ({cfg['curriculum']['n_incidents']} incidents, "
          f"{cfg['curriculum']['n_stages']} stages, "
          f"budget={cfg['curriculum']['total_sample_budget']} samples)")
    if args.show:
        for s in cfg["curriculum"]["stages"]:
            print(f"  stage {s['stage']}: +{len(s['newly_unlocked'])} new, "
                  f"{s['n_active']} active, {s['samples_this_stage']} samples")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
