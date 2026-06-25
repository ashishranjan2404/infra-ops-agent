"""D2 — RFT (GRPO/RLVR) launcher for a Qwen ~14B-class model on the opensre incident env.

Why this file exists
--------------------
A meeting requested running RFT on Qwen-14B because "8B may be too small" — the
opensre-qwen3-8b v2 run was flat/shallow (mean_reward ~0.50 -> ~0.54 over 15 steps,
runs/train_qwen3-8b_v2.jsonl). A larger base is the natural next lever.

This launcher is a thin, additive wrapper over the proven v2 trainer
(opensre-traj/train_rft_v2.py): same env (hud_env_v2.py, the P0 deterministic-judge
reward), same retry/spread/reset-head machinery. It does NOT edit the shared core
trainer; it imports it. The ONLY thing it changes is target-model selection plus a
preflight that refuses to run against a model that the HUD Tinker gateway does not
actually expose as trainable.

BLOCKER (documented, real — see D2/07_test_results.md and D2/09_critique.md)
---------------------------------------------------------------------------
As of 2026-06-25 `hud models list` exposes NO Qwen-14B (dense) in the Tinker
provider. Trainable Qwen dense sizes are: Qwen3.5-4B, Qwen3-8B, Qwen3.6-27B.
MoE trainables: Qwen3-30B-A3B, Qwen3.6-35B-A3B, Qwen3.5-397B-A17B. So a literal
"Qwen-14B" cannot be forked/trained on this backend today. This launcher therefore:
  (a) preflights the gateway and FAILS LOUD if the requested base is absent, and
  (b) defaults --base to the closest *available* dense upgrade from 8B
      (Qwen/Qwen3.6-27B), with Qwen/Qwen3-30B-A3B as the MoE alternative that was
      already partially trained (opensre-qwen3-30b).

Usage
-----
  set -a; source ~/.zshrc; set +a            # HUD_API_KEY
  HUD=../.venv-hud/bin

  # 0) preflight only — list trainable Qwen bases, verify the chosen base exists:
  $HUD/python train_rft_qwen14b.py --preflight

  # 1) fork a trainable head from the chosen base (once):
  $HUD/hud models fork Qwen/Qwen3.6-27B --name opensre-qwen14b-up
  #    -> emits a <slug>; pass it as --model below.

  # 2) smoke (cheap, fail-fast, no real grad step semantics relied on):
  $HUD/python train_rft_qwen14b.py --model <slug> --tasks 0,1 --group 4 --steps 1 --smoke

  # 3) real run (background, logs JSONL):
  $HUD/python train_rft_qwen14b.py --model <slug> \
      --tasks 0,1,2,3,4,5,6,7,8,9 --group 6 --steps 30 --reset-head \
      --out runs/train_qwen14b_v2.jsonl

This delegates the training loop to train_rft_v2.run(); see that file for the loop.
"""
from __future__ import annotations

import argparse
import asyncio
import os
import sys

# Resolve imports relative to the real opensre-traj package (this file lives under
# experiments/ralph_outputs/D2/artifacts/, the trainer lives in opensre-traj/).
_HERE = os.path.dirname(os.path.abspath(__file__))
_OPENSRE = os.path.abspath(os.path.join(_HERE, "..", "..", "..", "..", "opensre-traj"))

# Closest *available* dense upgrade from 8B (NO real 14B on the Tinker gateway).
DEFAULT_BASE = "Qwen/Qwen3.6-27B"
# Bases we consider acceptable "~14B-class or the documented substitute".
PREFERRED_BASES = [
    "Qwen/Qwen3.6-27B",       # dense, next dense rung above 8B
    "Qwen/Qwen3-30B-A3B",     # MoE ~3B active — cheap, already partially trained
    "Qwen/Qwen3.5-4B",        # smaller dense fallback if 27B is too costly
]


def _load_gateway_models():
    """Return list of (name, api_id, trainable_bool) from the HUD SDK, or raise."""
    sys.path.insert(0, _OPENSRE)
    from hud import models  # type: ignore
    # The SDK surface for listing varies by version; try the documented helper,
    # then fall back to shelling the CLI which is the stable contract.
    try:
        return models.list()  # type: ignore[attr-defined]
    except Exception:
        return None


def _cli_models_raw() -> str:
    import subprocess
    hud_bin = os.path.join(_OPENSRE, "..", ".venv-hud", "bin", "hud")
    env = dict(os.environ, COLUMNS="400")
    out = subprocess.run([hud_bin, "models", "list"], capture_output=True, text=True, env=env)
    return out.stdout + out.stderr


def preflight(requested_base: str | None) -> int:
    """List trainable Qwen bases; verify requested base is present + trainable."""
    raw = _cli_models_raw()
    qwen_lines = [ln for ln in raw.splitlines()
                  if "qwen" in ln.lower() and "tinker" in ln.lower()]
    trainable = [ln for ln in qwen_lines if "✓" in ln]
    print("=== Trainable Qwen bases on the HUD Tinker gateway ===")
    for ln in trainable:
        cells = [c.strip() for c in ln.strip("│").split("│")]
        if len(cells) >= 2:
            print(f"  - {cells[1]}")
    has_14b = any("14b" in ln.lower() for ln in trainable
                  if "a17b" not in ln.lower())  # exclude A17B false-positive
    print(f"\nQwen-14B (dense) present & trainable: {has_14b}")
    if not has_14b:
        print("BLOCKER: no Qwen-14B on this backend. Use the documented substitute "
              f"(default --base {DEFAULT_BASE}).")
    base = requested_base or DEFAULT_BASE
    present = any(base.lower() in ln.lower() for ln in trainable)
    print(f"Requested base '{base}' present & trainable: {present}")
    return 0 if present else 2


async def _run_training(args) -> int:
    sys.path.insert(0, _OPENSRE)
    os.chdir(_OPENSRE)  # hud_env_v2.py + runs/ are resolved relative to opensre-traj
    import train_rft_v2 as v2  # the proven core trainer (NOT modified)
    return await v2.run(args)


def main() -> int:
    ap = argparse.ArgumentParser(description="RFT launcher for a ~14B-class Qwen upgrade.")
    ap.add_argument("--model", help="trainable model slug from `hud models fork` (the forked head)")
    ap.add_argument("--base", default=DEFAULT_BASE,
                    help=f"base to fork/verify (default {DEFAULT_BASE}; no real 14B exists)")
    ap.add_argument("--preflight", action="store_true",
                    help="only list trainable Qwen bases + verify --base, then exit")
    ap.add_argument("--tasks", default="0,1,2,3,4,5,6,7,8,9")
    ap.add_argument("--group", type=int, default=6)
    ap.add_argument("--steps", type=int, default=30)
    ap.add_argument("--lr", type=float, default=1e-5)
    ap.add_argument("--reset-head", action="store_true")
    ap.add_argument("--out", default="")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()

    if args.preflight:
        return preflight(args.base)
    if not args.model:
        print("ERROR: --model <forked-slug> required for a real/smoke run "
              "(run --preflight first, then `hud models fork`).", file=sys.stderr)
        return 2
    # Guard: refuse to silently train against a vanished base.
    rc = preflight(args.base)
    if rc != 0 and not args.smoke:
        print("ERROR: base not trainable on gateway; aborting (see BLOCKER above).",
              file=sys.stderr)
        return rc
    return asyncio.run(_run_training(args))


if __name__ == "__main__":
    raise SystemExit(main())
