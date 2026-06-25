#!/usr/bin/env python3
"""A2 — 750-episode ablation with a FASTER/cheaper proposer model.

Background
----------
The canonical ablation is 5 conditions x 30 incidents (10 simple / 10 cascade /
10 novel) x 5 seeds = 750 episodes, scored with the P0 DETERMINISTIC judge
(rex/scoring.py, no LLM judge -> reproducible). The prior glm-5p2 run
(experiments/results/ablation_pass_at_k_glm-5p2.json.partial) was killed at
175/750 episodes (loop wrapper SIGTERM, rc=143) before the expensive REx /
rex_no_oracle conditions ran at all.

What this runner adds (without touching any shared core file)
-------------------------------------------------------------
1. A faster default proposer (`deepseek-v4-pro`, ~2-8 s/call via the HUD gateway,
   reliably parses & scores) instead of the slower full sweep.
2. A WALL-CLOCK time budget (`--max-seconds`): the run stops cleanly when the
   budget is exhausted and ALWAYS flushes the checkpoint, so a Ralph-loop
   SIGTERM can never lose progress. Re-running resumes from the checkpoint
   (rex.eval_pass_at_k.run_eval already supports `ckpt=`).
3. A partial-aware reporter: prints pass@k for whatever completed, plus an
   honest "completed N / 750" line so a blocked run reports real numbers, never
   fabricated ones.

It is a THIN WRAPPER: it imports rex.eval_pass_at_k.run_eval / print_report and
only schedules + time-boxes them. No shared file is modified.

Usage
-----
    set -a; source ~/.zshrc; set +a            # ANTHROPIC/FIREWORKS/HUD keys
    python3 experiments/ralph_outputs/A2/artifacts/run_ablation_fast.py \
        --model deepseek-v4-pro --per-family 10 --seeds 5 --max-seconds 1200

Output: experiments/ralph_outputs/A2/artifacts/ablation_pass_at_k_<model>.json
        (+ .partial checkpoint while running)
"""
from __future__ import annotations

import argparse
import json
import os
import signal
import sys
import time

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))))   # artifacts/A2/ralph_outputs/experiments/rl
sys.path.insert(0, REPO)

from rex.eval_pass_at_k import run_eval, print_report, CONDITIONS  # noqa: E402

OUTDIR = os.path.dirname(os.path.abspath(__file__))
ALL_CONDITIONS = ["zero_shot", "best_of_n", "retry_realistic", "rex", "rex_no_oracle"]


class _Deadline:
    """Install a SIGALRM so an over-budget run raises inside run_eval's thread
    pool driver; run_eval's `finally`-style checkpoint flush (it writes the ckpt
    at the end and every 25 episodes) preserves progress. We also re-raise as
    KeyboardInterrupt-equivalent so the outer handler writes a final partial."""

    def __init__(self, seconds: float):
        self.seconds = seconds

    def __enter__(self):
        if self.seconds and hasattr(signal, "SIGALRM"):
            signal.signal(signal.SIGALRM, self._fire)
            signal.alarm(int(self.seconds))
        return self

    def _fire(self, *_):
        raise TimeoutError(f"wall-clock budget of {self.seconds}s exhausted")

    def __exit__(self, *exc):
        if hasattr(signal, "SIGALRM"):
            signal.alarm(0)
        return False


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="deepseek-v4-pro",
                    help="faster/cheaper proposer (default: deepseek-v4-pro)")
    ap.add_argument("--per-family", type=int, default=10)
    ap.add_argument("--seeds", type=int, default=5)
    ap.add_argument("--conditions", default=",".join(ALL_CONDITIONS))
    ap.add_argument("--max-workers", type=int, default=8)
    ap.add_argument("--max-seconds", type=float, default=0.0,
                    help="wall-clock budget; 0 = unlimited")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    conditions = [c.strip() for c in args.conditions.split(",") if c.strip()]
    for c in conditions:
        if c not in CONDITIONS:
            ap.error(f"unknown condition {c!r}; known: {list(CONDITIONS)}")

    out_path = args.out or os.path.join(OUTDIR, f"ablation_pass_at_k_{args.model}.json")
    ckpt = out_path + ".partial"
    target = len(conditions) * (3 * args.per_family) * args.seeds

    print(f"=== A2 fast ablation: model={args.model} target={target} episodes "
          f"({len(conditions)} cond x {3*args.per_family} inc x {args.seeds} seeds) "
          f"budget={args.max_seconds or 'unlimited'}s ===", flush=True)

    t0 = time.time()
    completed = False
    out = None
    try:
        with _Deadline(args.max_seconds):
            out = run_eval(args.model, conditions, args.per_family, args.seeds,
                           max_workers=args.max_workers, label=f"{args.model} (A2)",
                           ckpt=ckpt)
        completed = True
    except (TimeoutError, KeyboardInterrupt) as e:
        print(f"\n[stopped] {type(e).__name__}: {e}", flush=True)
        out = _summarize_partial(ckpt, args.model, conditions, args.per_family, args.seeds)

    if out is None:
        # time-boxed out before the first 25-episode checkpoint flush: emit an
        # honest empty-but-valid report rather than crash (the smoke-test bug).
        print("[partial] no checkpoint yet — emitting empty report (0 completed)", flush=True)
        out = {"model": args.model, "label": f"{args.model} (A2 partial)",
               "threshold": 0.8, "seeds": args.seeds, "by_condition": {},
               "incidents_by_family": {}, "errors": [], "n_errors": 0,
               "floor_check": {"floor_ok": None}, "elapsed_s": None}

    done = _count_done(out)
    out["a2_meta"] = {"target_episodes": target, "completed_episodes": done,
                      "fully_completed": completed,
                      "wall_seconds": round(time.time() - t0, 1),
                      "fast_model": args.model,
                      "note": ("full 750-episode sweep" if completed and target == 750
                               else "partial / time-boxed run; numbers are real for "
                                    "completed episodes only")}
    if out.get("by_condition") and "floor_check" in out:
        print_report(out)
    print(f"\n[a2] completed {done}/{target} episodes "
          f"({'FULL' if completed else 'PARTIAL'}) in {out['a2_meta']['wall_seconds']}s")
    json.dump(out, open(out_path, "w"), indent=2)
    if completed and os.path.exists(ckpt):
        os.remove(ckpt)
    print(f"-> {out_path}")
    return 0


def _count_done(out: dict) -> int:
    n = 0
    for cond, d in out.get("by_condition", {}).items():
        for name, rs in d.get("per_incident_rewards", {}).items():
            n += len(rs)
    return n


def _summarize_partial(ckpt, model, conditions, per_family, seeds):
    """Build a normal report dict from the checkpoint's raw rewards so a
    time-boxed run still emits real pass@k for whatever finished."""
    if not os.path.exists(ckpt):
        return None
    from rex.eval_pass_at_k import summarize, pick_incidents
    raw = json.load(open(ckpt)).get("raw", {})
    incidents = pick_incidents(per_family)
    flat = [n for f in incidents.values() for n in f]
    out = {"model": model, "label": f"{model} (A2 partial)", "threshold": 0.8,
           "seeds": seeds, "incidents_by_family": incidents, "elapsed_s": None,
           "errors": [], "n_errors": 0, "by_condition": {}}
    for cond in conditions:
        cr = raw.get(cond, {})
        all_rewards = [r for name in flat for r in cr.get(name, [])]
        per_fam = {}
        for f, names in incidents.items():
            fr = [r for name in names for r in cr.get(name, [])]
            if fr:
                per_fam[f] = summarize(fr)
        out["by_condition"][cond] = {
            "overall": summarize(all_rewards) if all_rewards else summarize([0.0]),
            "by_family": per_fam,
            "per_incident_rewards": {name: cr.get(name, []) for name in flat},
        }
    # floor_check needs scenarios; reuse the real one (cheap, deterministic)
    from rex.eval_pass_at_k import floor_check
    out["floor_check"] = floor_check(flat)
    return out


if __name__ == "__main__":
    raise SystemExit(main())
