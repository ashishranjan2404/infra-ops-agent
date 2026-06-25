# 07 — Test Results

## 1. `make -n` dry-run on EVERY target (PASS)
All 11 targets emit a well-formed command. Selected output:

```
$ make -n test
cd /Users/mei/rl && python3 -m pytest -q tests

$ make -n eval
cd /Users/mei/rl && python3 -m rex.eval_pass_at_k \
  --model glm-5p2 --conditions zero_shot,best_of_n,retry_realistic,rex,rex_no_oracle \
  --per-family 5 --seeds 5 --max-workers 8

$ make -n eval-smoke
cd /Users/mei/rl && python3 -m rex.eval_pass_at_k \
  --model glm-5p2 --conditions zero_shot,rex --per-family 1 --seeds 1 --max-workers 2

$ make -n eval-frontier
cd /Users/mei/rl && python3 -m rex.eval_pass_at_k \
  --frontier --per-family 5 --seeds 5 --max-workers 8

$ make -n train
cd /Users/mei/rl/opensre-traj && /Users/mei/rl/.venv-hud/bin/python train_rft.py \
  --model opensre-qwen3-8b --tasks 0,1,3,10 --group 6 --steps 30 \
  --out runs/train_opensre-qwen3-8b.jsonl

$ make -n train-smoke
cd /Users/mei/rl/opensre-traj && /Users/mei/rl/.venv-hud/bin/python train_rft.py \
  --model opensre-qwen3-8b --tasks 0,1 --group 4 --steps 1 --smoke

$ make -n generate-scenarios
cd /Users/mei/rl && python3 experiments/build_incidents.py

$ make -n validate-scenarios
cd /Users/mei/rl && python3 experiments/build_incidents.py --validate

$ make -n figures
cd /Users/mei/rl && python3 -m rex.chart
cd /Users/mei/rl && python3 experiments/generate_table_pngs.py

$ make -n clean
cd /Users/mei/rl && find . -type d -name __pycache__ -not -path './.venv*/*' \
  -exec rm -rf {} + 2>/dev/null || true
```
`REPO` auto-resolved to `/Users/mei/rl` from the artifacts dir. PASS.

## 2. Flag-existence proof (PASS)
```
$ grep add_argument rex/eval_pass_at_k.py
  --model --conditions --per-family --seeds --max-workers --frontier --out    ✓
$ grep add_argument opensre-traj/train_rft.py
  --model --tasks --group --steps --out --smoke                               ✓
$ build_incidents.py  -> accepts --validate                                   ✓
```
Every flag emitted by the Makefile exists in the target script's argparse.

## 3. `make help` (PASS) — lists all 11 targets with descriptions.

## 4. `make validate-scenarios` — REAL RUN (PASS)
```
cd /Users/mei/rl && python3 experiments/build_incidents.py --validate
VALIDATION: 32/32 runnable (fix resolves & scores>=0.8, trap fails, gold diagnosis credited)
  cascade  14 ok / 0 bad
  novel    10 ok / 0 bad
  simple    8 ok / 0 bad
```

## 5. `make test` — REAL RUN (PASS)
```
cd /Users/mei/rl && python3 -m pytest -q tests
93 passed, 4 skipped in 0.16s
```

## Not executed (honest)
- `eval`, `eval-smoke`, `eval-frontier`: route through the HUD gateway → need
  `HUD_API_KEY` + cost money. Validated by dry-run + flag check only.
- `train`, `train-smoke`: need `.venv-hud` + a forked Qwen slug + HUD Tinker
  provider. Validated by dry-run + argparse check only.
- `figures`: depends on `rex/runs/curriculum.json` existing first. Dry-run only.

## Fixes applied during testing
None needed — `make -n` was correct on the first pass and both real targets
(test, validate-scenarios) passed clean.
