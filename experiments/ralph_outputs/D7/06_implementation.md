# D7 — 06 Implementation

## What I built (all task-namespaced; NO shared core edits)

### 1. `artifacts/d7_cascade_only.yaml` — cascade-only training config
The deliverable config. Declares the frozen-LLM "training" regime: exemplar pool drawn
**exclusively from the cascade family** (`train_family: cascade`, `n_exemplars: 3`),
eval on `[simple, cascade]`, baselines `[mixed, none]`, deterministic-judge
`pass_threshold: 0.8`. Header documents that this is an in-context proxy for an RFT
data-mix ablation (not gradient training) and states the H1/H2 hypotheses.

### 2. `artifacts/d7_train_eval.py` — train + transfer eval harness
- **Exemplar pool = "training set".** `make_exemplar` builds `(symptom, gold_root,
  gold_action)` from the registry; `render_exemplars` renders a few-shot prefix.
- **Three configs:** `cascade` (cascade-only pool), `mixed` (all families, eval-subtracted),
  `none` (zero-shot). `exemplar_block_for` builds each pool.
- **`make_proposer`** prepends the exemplar block to the existing core
  `build_prompt(scenario)` and calls the frozen model via `agent.llm.call`. Core
  prompt builder is reused unchanged.
- **`build_split`** draws train names from the cascade pool and removes them from every
  eval family (**hard leakage guard**); deterministic via `Random(1337)`.
- **`eval_family`** runs `run_plan` + `score_plan` (deterministic judge) per
  incident×seed, computes pass@1, Wilson CI, mean, std.
- **`run`** assembles the result object + transfer deltas H1/H2.
- **`--dry-run`** path: deterministic stand-in reward, **zero network** — validates
  split/leakage/scoring wiring without spending tokens.
- **YAML resilience:** `load_yaml` falls back to a built-in `_mini_yaml` parser if
  `pyyaml` is absent, so the harness runs standalone.

### Shared-core interaction
Imports are **read-only**: `rex.harness` (`scenarios_by_family`, `load_scenario`,
`run_plan`), `rex.loop` (`build_prompt`, `parse_plan`), `rex.scoring` (`score_plan`),
`compute_pass_at_k` (`wilson_ci`, `binary_pass`), `agent.llm.call`. One private read of
`rex.harness._SCENARIOS` (documented in 05) to obtain `symptom`/`gold_root`, which have
no public accessor. **No core file is modified or monkey-patched.** No `.patch` against
core was needed — the experiment is fully expressible as an additive wrapper.

## Outputs produced
- `artifacts/d7_results_dryrun.json` — zero-network wiring/leakage validation.
- `artifacts/d7_results_smoke.json` — REAL reduced LLM run (glm-5p2), real pass@1+CI.
- `artifacts/d7_smoke.yaml` — reduced config used for the real run.

## How to reproduce the full sweep (when compute allows)
```bash
set -a; source ~/.zshrc; set +a
python3 experiments/ralph_outputs/D7/artifacts/d7_train_eval.py \
  --config experiments/ralph_outputs/D7/artifacts/d7_cascade_only.yaml \
  --out    experiments/ralph_outputs/D7/artifacts/d7_results.json
```
Scale `n_eval_incidents`/`seeds` in the YAML to tighten the Wilson CIs.
