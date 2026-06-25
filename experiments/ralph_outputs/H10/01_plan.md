# 01 — Plan (H10: Makefile for common operations)

## Objective
Provide a single, discoverable entrypoint (`make <target>`) for the common
operations of the SRE-Degrees / REx project — test, eval, train, generate &
validate scenarios, figures — wired to the **actual** repo commands so a new
contributor can run them without spelunking docstrings.

## Approach
- Audit the real entrypoints and their flags first (no inventing commands):
  - tests: `pytest tests/`
  - eval: `python3 -m rex.eval_pass_at_k` (flags `--model --conditions
    --per-family --seeds --max-workers --frontier`)
  - train: `opensre-traj/train_rft.py` via `.venv-hud/bin/python` (HUD Tinker)
  - generate/validate scenarios: `experiments/build_incidents.py [--validate]`
  - figures: `python3 -m rex.chart` + `experiments/generate_table_pngs.py`
- Auto-resolve the repo root from the Makefile's own location so it works no
  matter where it's copied (artifacts dir is 4 levels below repo root).
- Make every target overridable (`MODEL=`, `PER_FAMILY=`, `SEEDS=`, ...).
- Add a `help` target (self-documenting via `## ` comments) and an `eval-smoke`
  fast path.

## Files to create
- `artifacts/Makefile` — the deliverable.
- The 10 step docs + SUMMARY.md + result.json.

## Dependencies / assumptions
- GNU make (present: /usr/bin/make). `just` is NOT installed → ship a Makefile,
  not a justfile (brief allows "Makefile / justfile").
- HUD_API_KEY needed for eval/train/frontier (gateway + Tinker). Documented.
- `.venv-hud` (py3.12) for HUD/training; repo default is py3.13.

## Risks
- Targets that hit the gateway cost money / need keys → cannot run for real in
  CI; mitigate with `make -n` dry-run validation + cheap real targets
  (`validate-scenarios`, `test`) actually executed.
- `python3 -m rex.*` only resolves from repo root → every recipe `cd $(REPO)`.

## Success criteria
- `make -n <target>` emits the correct command line for ALL targets.
- The 2 cheap targets (`validate-scenarios`, `test`) actually run.
- Flags used exist in the underlying scripts (verified by grep on argparse).
- No shared core file edited.
