# D7 — 04 Spec

## Files
- `artifacts/d7_cascade_only.yaml` — config (data only).
- `artifacts/d7_train_eval.py` — harness (no shared-core edits).
- `artifacts/d7_results.json` — output (real run); `d7_results_dryrun.json`,
  `d7_results_smoke.json` — validation outputs.

## Config schema (`d7_cascade_only.yaml`)
| key | type | meaning |
|---|---|---|
| `name` | str | config id |
| `train_family` | str | family the exemplar pool is drawn from (`cascade`) |
| `n_exemplars` | int | # in-context exemplars (capped at family size − 1) |
| `eval_families` | list[str] | families to eval pass@1 on (`[simple, cascade]`) |
| `n_eval_incidents` | int | held-out incidents per family |
| `seeds` | int | independent samples per incident |
| `model` | str | frozen proposer (gateway slug) |
| `temperature`/`max_tokens` | num | sampling params |
| `baselines` | list[str] | extra configs to contrast (`[mixed, none]`) |
| `pass_threshold` | float | deterministic-judge binary-pass cutoff (0.8) |
| `no_leakage` | bool | declared guard (enforced in code) |

## Data structures
```python
Exemplar = {"name": str, "family": str, "symptom": str,
            "gold_action": list[str], "gold_root": str}
Split    = {"train_names": list[str], "eval_sets": {family: [name, ...]}}
CellResult = {"n": int, "passes": int, "pass@1": float, "ci95": [lo, hi],
              "mean_reward": float, "reward_std": float, "eval_incidents": [str]}
```

## Function signatures
```python
make_exemplar(name: str) -> Exemplar
render_exemplars(exemplars: list[Exemplar]) -> str        # few-shot prefix text
make_proposer(model, exemplar_block, temp, max_tokens) -> propose(scenario, fb) -> plan
build_split(cfg: dict, rng: Random) -> Split              # leakage guard inside
exemplar_block_for(config_name, train_names, cfg, rng) -> str   # cascade|mixed|none
eval_family(propose, names, seeds, threshold, dry_run) -> CellResult
run(cfg: dict, dry_run: bool, model_override) -> dict     # full result object
```

## Output contract (`d7_results.json`)
```json
{
  "_meta": {"model","dry_run","train_family","n_exemplars","train_names",
            "configs","seeds","n_eval_incidents","threshold"},
  "cascade": {"simple": CellResult, "cascade": CellResult},
  "mixed":   {"simple": CellResult, "cascade": CellResult},
  "none":    {"simple": CellResult, "cascade": CellResult},
  "transfer": {"H1_helps_cascade_vs_none": float,
               "H2_hurts_simple_vs_mixed": float,
               "cascade_only"/"mixed"/"none": {"simple_p1","cascade_p1"},
               "note": str}
}
```

## Hypotheses
- **H1 (helps cascade):** `p1(cascade|train=cascade) ≥ p1(cascade|train=none)` → H1 delta ≥ 0.
- **H2 (hurts simple):** `p1(simple|train=cascade) < p1(simple|train=mixed)` → H2 delta < 0.

## Test cases
1. **YAML parse** — `yaml.safe_load` succeeds AND mini-YAML fallback yields same keys.
2. **py_compile** — harness compiles.
3. **Leakage** — `set(train_names) ∩ set(eval_incidents) == ∅` for every family.
4. **Determinism** — fixed `Random(1337)` split → identical `train_names` across runs.
5. **Dry-run** — produces full result object with no network; CI bounds in [0,1].
6. **Real smoke** — reduced budget → real pass@1 per cell, transfer deltas computed.

## API contract with shared core (READ-ONLY)
- `scenarios_by_family() -> {family: [name]}`
- `load_scenario(name) -> Scenario` (has `.prompt_text`)
- `run_plan(plan, scenario) -> sim`; `score_plan(plan, scenario, sim) -> (score, _)`
- `build_prompt(scenario, fb) -> str`; `parse_plan(text) -> plan`
- `wilson_ci(p, n)`, `binary_pass(r, thr)` from `compute_pass_at_k`
- `agent.llm.call(model, prompt, max_tokens, temperature) -> str`
No core symbol is reassigned or monkey-patched.
