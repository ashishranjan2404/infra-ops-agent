# H10 — Summary: Makefile for common operations

## Deliverable
`experiments/ralph_outputs/H10/artifacts/Makefile` — a 126-line GNU make file
giving the SRE-Degrees / REx project a single discoverable entrypoint for its
common operations, wired to the actual repo commands.

## Targets (11, all .PHONY, all `## `-documented)
| Target | Real command |
|---|---|
| help (default) | self-documenting list |
| test | python3 -m pytest -q tests |
| eval | python3 -m rex.eval_pass_at_k (deterministic judge, full ablation) |
| eval-smoke | tiny fast eval (1/family, 1 seed) |
| eval-frontier | rex.eval_pass_at_k --frontier |
| train | .venv-hud/bin/python opensre-traj/train_rft.py ... |
| train-smoke | fail-fast 2-task/1-step smoke |
| generate-scenarios | python3 experiments/build_incidents.py |
| validate-scenarios | ... build_incidents.py --validate |
| figures | rex.chart + experiments/generate_table_pngs.py |
| clean | scoped __pycache__ purge (excludes .venv*) |

## Validation (07)
- make -n on ALL 11 targets -> correct command lines; REPO auto-resolves to /Users/mei/rl.
- Every emitted flag verified to exist in the target script's argparse.
- Real runs: make test -> 93 passed / 4 skipped; make validate-scenarios -> 32/32 scenarios runnable.
- Not run (need gateway key / forked model / prior data, honestly documented): eval*, train*, figures.

## Compliance
No shared core file edited. All outputs are new, task-namespaced files under
experiments/ralph_outputs/H10/.
