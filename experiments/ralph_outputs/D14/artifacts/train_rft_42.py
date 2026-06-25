#!/usr/bin/env python3
"""D14 — config-driven RFT (GRPO) launcher over the full 42-incident benchmark.

Unlike opensre-traj/train_rft_v2.py (which trains on a 0-based INDEX slice into the
34 canonical `Taskset.from_module` tasks, defaulting to the first 10), this launcher
builds its Taskset from EXPLICIT scenario_ids in tasks_42.json. That matters because
the 42-set deliberately includes 8 held-out *variant* scenario_ids that are NOT in
`canonical_ids()` and therefore are unreachable by integer index.

It is intentionally ADDITIVE and task-namespaced: it imports the existing
`hud_env_v2.investigate_v2` template + the `SCENARIOS` corpus and constructs tasks
directly. It does NOT modify any shared core file.

Run:
    set -a; source ~/.zshrc; set +a
    ../../../../.venv-hud/bin/python train_rft_42.py --config train_rft_42.yaml --smoke
    ../../../../.venv-hud/bin/python train_rft_42.py --config train_rft_42.yaml

Dry-run (no HUD / no network — validates config + task resolution + curriculum):
    python3 train_rft_42.py --config train_rft_42.yaml --dry-run
"""
from __future__ import annotations

import argparse
import asyncio
import json
import os
import statistics as st
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]                       # /Users/mei/rl
OPENSRE = REPO / "opensre-traj"


def _load_yaml(path: Path) -> dict:
    try:
        import yaml  # pyyaml is in requirements-rex.txt
        return yaml.safe_load(path.read_text())
    except ModuleNotFoundError:
        raise SystemExit("pyyaml not installed; pip install pyyaml (it is in requirements-rex.txt)")


def load_config(path: Path, smoke: bool) -> dict:
    cfg = _load_yaml(path)
    if smoke and isinstance(cfg.get("smoke"), dict):
        cfg = {**cfg, **cfg["smoke"]}        # smoke overrides win
    return cfg


def resolve_task_ids(cfg: dict, cfg_dir: Path) -> tuple[list[str], list[dict]]:
    task_file = (cfg_dir / cfg["task_file"]).resolve()
    payload = json.loads(task_file.read_text())
    rows = payload["tasks"]

    sel = cfg.get("tasks", "all")
    if sel != "all" and sel is not None:
        idx = [int(i) for i in str(sel).split(",")]
        rows = [rows[i] for i in idx]

    if cfg.get("curriculum"):
        rows = sorted(rows, key=lambda r: (r.get("difficulty", 3), r.get("index", 0)))

    return [r["scenario_id"] for r in rows], rows


def build_tasks(scenario_ids: list[str]):
    """Construct HUD tasks from explicit scenario_ids using the existing v2 template."""
    sys.path.insert(0, str(OPENSRE))
    os.chdir(OPENSRE)                          # SCENARIOS corpus path is relative to cwd
    import hud_env_v2 as env                   # additive import; does not modify it
    from hud_env import SCENARIOS

    missing = [s for s in scenario_ids if s not in SCENARIOS]
    if missing:
        raise SystemExit(f"{len(missing)} scenario_ids absent from corpus: {missing[:5]}")
    return [env.investigate_v2(scenario_id=s) for s in scenario_ids], env


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
            print(f"  [retry {attempt}/{tries}] {what} transient ({msg[:60]}); sleep {wait}s")
            await asyncio.sleep(wait)


async def run(cfg: dict, scenario_ids: list[str], rows: list[dict], model: str) -> int:
    from hud import Job, Taskset, TrainingClient
    from hud.agents import create_agent

    hud_tasks, _env = build_tasks(scenario_ids)
    ts = Taskset(name=f"{cfg['name']}-{model}", tasks=hud_tasks)
    group = int(cfg.get("group", 6))
    steps = int(cfg.get("steps", 30))
    lr = float(cfg.get("learning_rate", 1e-5))
    smoke = bool(cfg.get("_smoke"))
    print(f"{cfg['name']}  model={model}  n_tasks={len(hud_tasks)}  group={group}  "
          f"steps={steps}  lr={lr}  curriculum={cfg.get('curriculum')}")

    agent = create_agent(model, completion_kwargs={"extra_body": {"return_token_ids": True}})
    trainer = TrainingClient(model)

    if cfg.get("reset_head") and not smoke:
        try:
            cps = await trainer.checkpoints()
            if cps:
                await trainer.set_head(cps[0].id)
                print(f"reset head -> {getattr(cps[0], 'name', cps[0].id)}")
        except Exception as e:  # noqa: BLE001
            print(f"reset-head skipped ({type(e).__name__}: {str(e)[:80]})")

    session = await Job.start(model, group=group)
    print(f"job: https://hud.ai/jobs/{session.id}")

    logf = cfg.get("out")
    if logf:
        os.makedirs(os.path.dirname(logf) or ".", exist_ok=True)

    for step in range(steps):
        start = len(session.runs)
        await _aretry(lambda: ts.run(agent, group=group, job=session), f"rollouts@{step}")
        batch = session.runs[start:]
        rewards = [r.reward for r in batch]
        mean_r = sum(rewards) / len(rewards) if rewards else 0.0
        spread = st.pstdev(rewards) if len(rewards) > 1 else 0.0
        res = await _aretry(
            lambda: trainer.step(batch, learning_rate=lr, group_size=group), f"step@{step}")
        line = {"step": step, "mean_reward": round(mean_r, 4), "reward_std": round(spread, 4),
                "n": len(batch), "loss": getattr(res, "loss", None)}
        print(f"step {step:>3}  mean_reward={mean_r:.4f}  spread={spread:.3f}  n={len(batch)}")
        if logf:
            with open(logf, "a") as fh:
                fh.write(json.dumps(line) + "\n")
    print("DONE" if not smoke else "SMOKE OK")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--model", default=None, help="override model slug from config")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--dry-run", action="store_true",
                    help="resolve config + tasks + curriculum offline; no HUD calls")
    args = ap.parse_args()

    cfg_path = Path(args.config).resolve()
    cfg = load_config(cfg_path, smoke=args.smoke)
    cfg["_smoke"] = args.smoke
    model = args.model or cfg.get("model")
    scenario_ids, rows = resolve_task_ids(cfg, cfg_path.parent)

    if args.dry_run:
        order = [(r["scenario_id"], r.get("difficulty")) for r in rows]
        print(f"[dry-run] config={cfg_path.name}  model={model}")
        print(f"[dry-run] resolved {len(scenario_ids)} tasks "
              f"(group={cfg.get('group')}, steps={cfg.get('steps')}, lr={cfg.get('learning_rate')})")
        # validate every id exists in the corpus WITHOUT importing hud_env (which pulls
        # in the `hud` package, only installable in .venv-hud) — read the corpus directly.
        corpus_path = OPENSRE / "out" / "trajectories.jsonl"
        corpus_ids = set()
        with corpus_path.open() as fh:
            for line in fh:
                line = line.strip()
                if line:
                    corpus_ids.add(json.loads(line)["scenario_id"])
        missing = [s for s in scenario_ids if s not in corpus_ids]
        print(f"[dry-run] corpus has {len(corpus_ids)} scenarios; missing={missing}")
        print(f"[dry-run] curriculum order (first 6): {order[:6]}")
        if missing:
            return 1
        print("[dry-run] OK: config valid, all 42 scenario_ids resolve in corpus")
        return 0

    if not model:
        raise SystemExit("no model: set `model:` in config or pass --model")
    return asyncio.run(run(cfg, scenario_ids, rows, model))


if __name__ == "__main__":
    raise SystemExit(main())
