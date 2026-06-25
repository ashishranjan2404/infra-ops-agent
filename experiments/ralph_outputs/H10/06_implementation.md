# 06 — Implementation

## What I built
`experiments/ralph_outputs/H10/artifacts/Makefile` (126 lines, GNU make).
Self-locating repo root, self-documenting `help`, 11 `.PHONY` targets all wired
to the project's real entrypoints.

### Targets
| Target | Underlying real command |
|---|---|
| `help` | self-doc from `## ` comments (default goal) |
| `test` | `python3 -m pytest -q tests` |
| `eval` | `python3 -m rex.eval_pass_at_k` (deterministic judge, full ablation) |
| `eval-smoke` | same, 1 incident/family, 1 seed, `zero_shot,rex` |
| `eval-frontier` | `python3 -m rex.eval_pass_at_k --frontier` |
| `train` | `.venv-hud/bin/python opensre-traj/train_rft.py ...` |
| `train-smoke` | `train_rft.py --tasks 0,1 --group 4 --steps 1 --smoke` |
| `generate-scenarios` | `python3 experiments/build_incidents.py` |
| `validate-scenarios` | `python3 experiments/build_incidents.py --validate` |
| `figures` | `python3 -m rex.chart` + `experiments/generate_table_pngs.py` |
| `clean` | scoped `find ... __pycache__` (excludes `.venv*`) |

### Key implementation details
- **Repo-root auto-detection:** `MAKEFILE_PATH := $(abspath $(lastword
  $(MAKEFILE_LIST)))` then `REPO ?= $(abspath $(dir $(MAKEFILE_PATH))/../../../..)`.
  The artifacts dir is 4 levels under the repo root; resolves to `/Users/mei/rl`.
  Overridable with `make REPO=/path ...`.
- **Every recipe `cd $(REPO) &&`** so `python3 -m rex.*` and relative script
  paths resolve (rex is a package only from the root; verified the bare
  `python3 -m rex.eval_pass_at_k` fails from elsewhere and succeeds from root).
- **All flags verified against the scripts' argparse** (see 07): the eval flags
  `--model/--conditions/--per-family/--seeds/--max-workers/--frontier`, the
  train flags `--model/--tasks/--group/--steps/--out/--smoke`, and
  `build_incidents.py --validate` all exist.
- **Safety:** `clean` only touches `__pycache__`, excludes `.venv*`, `|| true`.

## Shared-core-file policy
No shared core file edited. The Makefile is a NEW, task-namespaced artifact under
`experiments/ralph_outputs/H10/artifacts/`. If the team wants it at the repo
root, it can be copied there unchanged (REPO auto-detect still works because it's
overridable, and at root the `../../../..` would need adjusting — documented in
09 as the one path-coupling caveat; the override flag covers it).

## Artifacts
- `artifacts/Makefile`
