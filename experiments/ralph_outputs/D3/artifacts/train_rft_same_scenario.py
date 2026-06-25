"""D3 — RFT driver with SAME-SCENARIO GRPO groups (proposed train_rft_v3).

This is an ADDITIVE copy of opensre-traj/train_rft_v2.py. It does NOT edit the
shared core file. The ONLY substantive change is the training loop: instead of
one `ts.run` over a multi-scenario Taskset (which lets a GRPO group mix
scenarios), we run ONE single-task Taskset per scenario per step, so every
`trainer.step` group is pure same-scenario.

  # smoke (needs ../.venv-hud and a forked model slug):
  #   set -a; source ~/.zshrc; set +a
  #   ../../../.venv-hud/bin/python train_rft_same_scenario.py \
  #       --model <slug> --tasks 0,1 --group 4 --steps 1 --smoke
  # real:
  #   ../../../.venv-hud/bin/python train_rft_same_scenario.py --model <slug> \
  #       --tasks 0,1,2,3,4,5,6,7,8,9 --group 6 --steps 30 --out runs/v3.jsonl

Diff vs train_rft_v2.py (documented for the maintainer to fold back into core):
  - build a SEPARATE single-task Taskset per scenario index;
  - per step, loop scenarios, call ts_i.run(group=G) -> a pure same-scenario batch;
  - compute + log per-scenario within-group spread; concatenate batches; ONE
    trainer.step over the union (group_size=G is honored because every contiguous
    G-block is one scenario);
  - log the cross-scenario reward spread we are deliberately NOT baselining over.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import os
import statistics as st
import sys

# local same-scenario utilities (works without HUD imported)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from same_scenario_groups import group_rollouts_by_scenario  # noqa: E402

ENV = os.environ.get("OPENSRE_ENV", "hud_env_v2.py")


async def _aretry(make_coro, what: str, tries: int = 6):
    for attempt in range(1, tries + 1):
        try:
            return await make_coro()
        except Exception as e:  # noqa: BLE001
            msg = str(e)
            transient = any(s in msg for s in ("502", "503", "504", "Temporarily", "Unavailable")) \
                or getattr(e, "status_code", None) in (500, 502, 503, 504)
            if attempt == tries or not transient:
                raise
            wait = min(30, 2 ** attempt)
            print(f"  [retry {attempt}/{tries}] {what} transient fail ({msg[:60]}); sleeping {wait}s")
            await asyncio.sleep(wait)


async def run(args) -> int:
    # HUD is imported lazily so `--help` / unit tests don't require the venv.
    from hud import Job, Taskset, TrainingClient
    from hud.agents import create_agent

    full = Taskset.from_module(ENV)
    items = [t for (_slug, t) in full.items()]
    idx = [int(i) for i in args.tasks.split(",")]
    # ONE single-scenario taskset per index — this is the crux of the fix.
    per_scenario_ts = [Taskset(name=f"opensre-v3-s{i}", tasks=[items[i]]) for i in idx]
    print(f"v3(same-scenario)  model={args.model}  scenarios={idx}  group={args.group}  "
          f"steps={args.steps}  lr={args.lr}  env={ENV}")

    agent = create_agent(args.model, completion_kwargs={"extra_body": {"return_token_ids": True}})
    trainer = TrainingClient(args.model)
    session = await Job.start(args.model, group=args.group)
    print(f"job: https://hud.ai/jobs/{session.id}")

    logf = args.out
    if logf:
        os.makedirs(os.path.dirname(logf) or ".", exist_ok=True)

    for step in range(args.steps):
        batch = []
        per_scenario_spreads = []
        scenario_means = []
        for i, ts_i in zip(idx, per_scenario_ts):
            start = len(session.runs)
            await _aretry(lambda ts=ts_i: ts.run(agent, group=args.group, job=session),
                          f"rollouts s{i}@{step}")
            sub = session.runs[start:]
            batch.extend(sub)
            rs = [r.reward for r in sub]
            spr = st.pstdev(rs) if len(rs) > 1 else 0.0
            per_scenario_spreads.append(round(spr, 4))
            scenario_means.append(round(sum(rs) / len(rs), 4) if rs else 0.0)
            if args.smoke:
                print(f"  [smoke] scenario {i}: n={len(sub)} rewards={[round(x,3) for x in rs]} "
                      f"within_spread={spr:.3f}")

        rewards = [r.reward for r in batch]
        mean_r = sum(rewards) / len(rewards) if rewards else 0.0
        # cross-scenario spread = the term we REMOVE from the advantage baseline.
        cross_spread = st.pstdev(scenario_means) if len(scenario_means) > 1 else 0.0
        mean_within = sum(per_scenario_spreads) / len(per_scenario_spreads) if per_scenario_spreads else 0.0

        # sanity: confirm groups really are same-scenario before stepping.
        groups = group_rollouts_by_scenario(batch)
        assert all(g.is_degenerate or g.reward_std >= 0 for g in groups)
        n_pure = len(groups)

        res = await _aretry(
            lambda: trainer.step(batch, learning_rate=args.lr, group_size=args.group),
            f"step@{step}")
        line = {"step": step, "mean_reward": round(mean_r, 4),
                "mean_within_scenario_spread": round(mean_within, 4),
                "cross_scenario_spread_removed": round(cross_spread, 4),
                "per_scenario_within_spread": per_scenario_spreads,
                "n_scenario_groups": n_pure, "n": len(batch),
                "loss": getattr(res, "loss", None)}
        print(f"step {step:>3}  mean_reward={mean_r:.4f}  within={mean_within:.3f}  "
              f"cross_removed={cross_spread:.3f}  groups={n_pure}  n={len(batch)}  loss={line['loss']}")
        if logf:
            with open(logf, "a") as fh:
                fh.write(json.dumps(line) + "\n")

    if args.smoke:
        print("SMOKE OK: per-scenario rollouts -> pure same-scenario groups -> step -> logged.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True, help="trainable model slug (from `hud models fork`)")
    ap.add_argument("--tasks", default="0,1,2,3,4,5,6,7,8,9", help="comma 0-based scenario indices")
    ap.add_argument("--group", type=int, default=6)
    ap.add_argument("--steps", type=int, default=30)
    ap.add_argument("--lr", type=float, default=1e-5)
    ap.add_argument("--out", default="")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    return asyncio.run(run(args))


if __name__ == "__main__":
    raise SystemExit(main())
