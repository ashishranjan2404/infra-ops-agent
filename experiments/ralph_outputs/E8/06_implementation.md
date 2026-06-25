# E8 — 06 Implementation

## Artifacts built (all under `experiments/ralph_outputs/E8/artifacts/`)
| file | what it is |
|---|---|
| `fireball_sweep.py` | the sweep harness: reader, stratified/nested subsetter, power analysis, sweep driver, gated learning-curve fitter, CLI |
| `make_fixture.py` | synthetic Fireball-format fixture generator (no score field) |
| `test_fireball_sweep.py` | 13 pytest tests incl. anti-fabrication guards |
| `fixture_corpus.jsonl` | generated 2000-record fixture (validation input) |
| `sweep_manifests/*.json` | per-(N,seed) subset manifests from the real-corpus sweep |

## Key implementation points
- **Reader** (`read_corpus`) is shape-tolerant (id/family/trajectory key fallbacks),
  de-dups on id, skips non-Fireball + blank lines, raises on malformed JSON.
- **Stratified subsetter** (`stratified_subset`) uses largest-remainder apportionment over
  `family::difficulty` strata; within a stratum records are ordered by a stable
  `sha256(seed:rid)` and a prefix is taken → deterministic + near-nested across N.
- **Power analysis** (`required_n_for_effect`) is closed-form with an inlined Acklam
  inverse-normal (no scipy/numpy). Returns **eval-rollout** per-arm N.
- **Sweep driver** (`run_sweep`) writes manifests and, only with a real `fit` callback,
  records (N, score). Without a callback: `blocked:true`, all scores None, no curve.
- **Curve fitter** (`fit_learning_curve`) refuses (<4 points → None); else grid-fits
  `score(N)=a-b·N^(-c)` and reports a 95%-asymptote knee. Never fed fabricated points in
  `result.json`.

## How to run
```bash
cd experiments/ralph_outputs/E8/artifacts
python3 -m pytest test_fireball_sweep.py -q          # 13 passed
python3 fireball_sweep.py --profile-only             # real-corpus profile + power N
python3 fireball_sweep.py --out-dir sweep_manifests  # full sweep (BLOCKED, caps at 319)
python3 make_fixture.py --n 2000                      # regenerate fixture
python3 fireball_sweep.py --corpus fixture_corpus.jsonl --n-grid 100,500,1000,2000 --seeds s1
```

## Proposed (NOT applied) change to shared core
To turn the sweep from BLOCKED → real, a fit callback must wrap the existing trainer +
evaluator. The natural wiring is: subset → write SFT/GRPO data → train a Qwen fork →
score via `rex.eval_pass_at_k` / `opensre-traj` HUD eval → return mean reward. This would
live in `opensre-traj/train_rft_v2.py` + `rex/eval_pass_at_k.py`, which are **shared core
files I did not edit**. The callback signature is already defined
(`FitCallback = (list[Record], str) -> float`) so a future PR injects it without changing
the harness. Documented here rather than patched, per the parallel-safety rules.
