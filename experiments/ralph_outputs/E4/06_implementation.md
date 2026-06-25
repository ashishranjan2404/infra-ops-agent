# E4 — 06 Implementation

## What I built (all under `experiments/ralph_outputs/E4/`, no shared-core edits)

### `artifacts/compare_simple8.py` (232 lines)
A self-contained "does it hurt?" comparison driver for the 8 simple incidents.
- Imports FROZEN REx primitives read-only: `load_scenario`, `run_plan`,
  `scenarios_by_family` (`rex.harness`); `build_prompt`, `parse_plan` (`rex.loop`);
  `score_plan` — the P0 deterministic judge (`rex.scoring`); and `pass_at_k`,
  `wilson_ci`, `binary_pass` (`experiments/compute_pass_at_k`).
- Pins `SIMPLE_8` and `validate_incidents()` fails fast if any is not in the live
  `simple` family.
- For two slugs, runs each zero-shot `--seeds` times/incident over a thread pool,
  grades with the deterministic judge, and emits per-incident pass@1, delta(B−A),
  a `hurts` flag, an overall verdict, Wilson CIs, and an in-band `note` caveat.

### `artifacts/test_compare_simple8.py` (6 offline tests)
Validates the pinned-8 are real simple-family incidents and the summarize/threshold
math — runs with no network.

### `run_standin.json`
Real output of the stand-in run (glm-5p2 vs minimax-m3), 0 errors.

## Proposed change to a shared core file: NONE
This task needed no modification to any `rex/*`, `sim/*`, `agent/*`, or
`experiments/*.py` file — the harness composes the existing public primitives, so no
`.patch` was necessary.

## How the real (un-blocked) run would be invoked
```
set -a; source ~/.zshrc; set +a
python3 artifacts/compare_simple8.py \
  --model-a <fireball-trained-slug> --label-a fireball \
  --model-b <opensre-grpo-slug>     --label-b opensre \
  --seeds 8 --out run_real.json
```
Both slugs must first be registered in `agent/models.py` ROSTER (fork via
`hud models fork ...` for the OpenSRE Qwen; the FIREBALL corpus + slug must be
supplied — see the blocker in 07/09).

## Stand-in run command actually executed
```
python3 compare_simple8.py --model-a glm-5p2 --label-a glm5p2_standin \
  --model-b minimax-m3 --label-b minimax_standin --seeds 3 \
  --out .../E4/run_standin.json
```
