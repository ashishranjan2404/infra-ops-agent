#!/usr/bin/env python3
"""D5 — SFT (behavioral cloning) leg of the RFT-vs-SFT comparison.

Mirrors the structure of opensre-traj/train_rft_v2.py but trains on SUPERVISED
(prompt -> completion) pairs from build_sft_data.py instead of advantage-weighted
rollouts. Same base model, same scenario split, same eval grader as the RFT leg, so
the two regimes are compared on IDENTICAL data.

HONEST SCAFFOLD (per 05_ouroboros C1): the HUD Tinker provider's TrainingClient is
designed around rollout batches (`trainer.step(batch_of_Runs, lr, group_size)`). A
supervised token-target step is a DIFFERENT API surface. Rather than fake a plausible
loss, this script introspects TrainingClient at the training call and raises a precise
NotImplementedError naming the missing method if supervised fine-tuning is unsupported.
Everything up to that point (data load, prompt render, batch build) is real and runs.

  # render full prompts (needs the HUD env importable, i.e. .venv-hud):
  set -a; source ~/.zshrc; set +a
  ../../../../.venv-hud/bin/python train_sft.py --model <slug> --data sft_pairs.jsonl --epochs 3 --smoke
"""
from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
OPENSRE = os.path.join(REPO, "opensre-traj")


def _load_pairs(path: str) -> list[dict]:
    rows = []
    with open(path) as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def _render_prompt(scenario_id: str) -> str:
    """Render the SAME STATIC_PROMPT the eval/RFT env uses, for this scenario.
    Requires the HUD env modules (opensre-traj on sys.path); only called when present."""
    sys.path.insert(0, OPENSRE)
    sys.path.insert(0, REPO)
    import json as _json
    from hud_env import SCENARIOS, CATEGORIES, _redact_alert
    from hud_env_static import STATIC_PROMPT, _evidence_text
    rec = SCENARIOS[scenario_id]
    return STATIC_PROMPT.format(
        cats=", ".join(CATEGORIES),
        alert=_json.dumps(_redact_alert(rec["alert"]), indent=2),
        evidence=_evidence_text(rec),
    )


def _build_supervised_batches(pairs: list[dict], render: bool) -> list[dict]:
    """Build (prompt, completion) examples. With --render, attach the full prompt;
    otherwise carry the prompt_ref (scenario_id) for offline structural validation."""
    batch = []
    for p in pairs:
        ex = {"scenario_id": p["scenario_id"], "completion": p["completion"]}
        ex["prompt"] = _render_prompt(p["scenario_id"]) if render else None
        batch.append(ex)
    return batch


async def run(args) -> int:
    pairs = _load_pairs(args.data)
    print(f"SFT  model={args.model}  pairs={len(pairs)}  epochs={args.epochs}  lr={args.lr}")

    # Real, runs offline: build the supervised batches.
    batch = _build_supervised_batches(pairs, render=args.render)
    print(f"built {len(batch)} supervised examples"
          + (" (prompts rendered)" if args.render else " (prompt_ref only; pass --render in .venv-hud)"))

    if args.dry:
        print("DRY: data + batch construction OK; skipping the HUD training call.")
        return 0

    # The training call — introspect the SDK for a supervised step.
    from hud import TrainingClient  # noqa
    trainer = TrainingClient(args.model)
    supervised_method = next(
        (m for m in ("supervised_step", "sft_step", "fit", "train_supervised")
         if hasattr(trainer, m)), None)
    if supervised_method is None:
        raise NotImplementedError(
            "hud.TrainingClient exposes no supervised token-target step "
            f"(checked: supervised_step/sft_step/fit/train_supervised; has: "
            f"{[a for a in dir(trainer) if not a.startswith('_')]}). "
            "The Tinker provider is rollout-batch oriented (trainer.step(batch_of_Runs, "
            "lr, group_size)). SFT requires a token-target endpoint — SDK-BLOCKED. "
            "See 07_test_results.md / 09_critique.md.")

    logf = args.out
    if logf:
        os.makedirs(os.path.dirname(logf) or ".", exist_ok=True)
    step = getattr(trainer, supervised_method)
    for epoch in range(args.epochs):
        res = await step(batch, learning_rate=args.lr)
        line = {"epoch": epoch, "mean_loss": getattr(res, "loss", None), "n": len(batch)}
        print(f"epoch {epoch}  loss={line['mean_loss']}  n={len(batch)}")
        if logf:
            with open(logf, "a") as fh:
                fh.write(json.dumps(line) + "\n")
        if args.smoke:
            print("SMOKE OK: supervised batch -> forward/backward -> loss logged.")
            break
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True, help="trainable base slug (SAME base as the RFT leg)")
    ap.add_argument("--data", default=os.path.join(HERE, "sft_pairs.jsonl"))
    ap.add_argument("--epochs", type=int, default=3)
    ap.add_argument("--lr", type=float, default=1e-5)
    ap.add_argument("--render", action="store_true", help="render full prompts (needs HUD env)")
    ap.add_argument("--dry", action="store_true", help="build data only, no HUD call (offline)")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--out", default="")
    args = ap.parse_args()
    return asyncio.run(run(args))


if __name__ == "__main__":
    raise SystemExit(main())
