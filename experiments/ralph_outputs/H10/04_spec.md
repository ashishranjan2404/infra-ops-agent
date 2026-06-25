# 04 — Technical Spec

## File
`experiments/ralph_outputs/H10/artifacts/Makefile` (GNU make syntax).

## Variables (overridable on the command line)
| Var | Default | Meaning |
|---|---|---|
| `REPO` | auto (`$(MAKEFILE_PATH)/../../../..`) | repo root |
| `PYTHON` | `python3` | interpreter for py3.13 targets |
| `PYTEST` | `$(PYTHON) -m pytest` | test runner |
| `MODEL` | `glm-5p2` | eval model slug |
| `CONDITIONS` | `zero_shot,best_of_n,retry_realistic,rex,rex_no_oracle` | ablation set |
| `PER_FAMILY` | `5` | incidents per family |
| `SEEDS` | `5` | episodes per incident |
| `MAX_WORKERS` | `8` | eval concurrency |
| `HUD_PY` | `$(REPO)/.venv-hud/bin/python` | py3.12 venv for HUD/training |
| `TRAIN_MODEL` | `opensre-qwen3-8b` | forked Qwen slug |
| `TRAIN_TASKS` | `0,1,3,10` | task indices |
| `TRAIN_GROUP` | `6` | GRPO group size |
| `TRAIN_STEPS` | `30` | training steps |

## Targets → command contract
| Target | Emitted command (from `$(REPO)`) |
|---|---|
| `help` | grep `## ` comments, pretty-print |
| `test` | `python3 -m pytest -q tests` |
| `eval` | `python3 -m rex.eval_pass_at_k --model M --conditions C --per-family P --seeds S --max-workers W` |
| `eval-smoke` | `... --conditions zero_shot,rex --per-family 1 --seeds 1 --max-workers 2` |
| `eval-frontier` | `python3 -m rex.eval_pass_at_k --frontier --per-family P --seeds S --max-workers W` |
| `train` | `(cd opensre-traj) .venv-hud/bin/python train_rft.py --model ... --tasks ... --group ... --steps ... --out runs/train_<slug>.jsonl` |
| `train-smoke` | `... --tasks 0,1 --group 4 --steps 1 --smoke` |
| `generate-scenarios` | `python3 experiments/build_incidents.py` |
| `validate-scenarios` | `python3 experiments/build_incidents.py --validate` |
| `figures` | `python3 -m rex.chart` ; `python3 experiments/generate_table_pngs.py` |
| `clean` | `find . -type d -name __pycache__ -not -path './.venv*/*' -exec rm -rf {} + || true` |

## Flag-existence proof obligations (verified in 07)
- `rex/eval_pass_at_k.py` argparse defines: `--model --conditions --per-family
  --seeds --max-workers --frontier --out`.
- `opensre-traj/train_rft.py` argparse defines: `--model --tasks --group
  --steps --out --smoke`.
- `experiments/build_incidents.py` accepts `--validate`.

## Acceptance test cases
1. `make -n <T>` for every T → emits a command whose argv flags all exist.
2. `make help` lists all targets with descriptions.
3. `make validate-scenarios` exits 0 and prints "N/N runnable".
4. `make test` collects & runs the pytest suite.
5. `make -n clean` shows a `find ... __pycache__` that excludes `.venv*`.
6. `REPO` resolves to `/Users/mei/rl` when run from the artifacts dir.
