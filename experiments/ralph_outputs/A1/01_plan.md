# A1 — Full 42-incident pass@k evaluation — PLAN

## Objective
Currently pass@k numbers are computed only on a 5-per-family slice (15 incidents) via
`python3 -m rex.eval_pass_at_k --per-family 5`. The benchmark actually contains **42
incidents** (12 simple + 20 cascade + 10 novel — confirmed via
`rex.harness.scenarios_by_family()`). Produce the **full 42-incident** pass@1/2/5 table
(with Wilson 95% CIs, per-family splits, within-group reward std, and the floor check)
for at least one model, reusing the existing deterministic-judge pipeline.

## Approach
The existing pipeline `rex/eval_pass_at_k.py` already supports the full set: passing
`--per-family 0` makes `pick_incidents(None)` return *all* incidents per family. So the
"work" is not new estimator code — it is (a) running the full sweep without truncation,
(b) doing it under the parallel-safety rules (no edits to shared `rex/*.py`, no writes
to the shared `experiments/results/` dir), and (c) handling the scale (5 conditions ×
42 incidents × 5 seeds, with REx/best-of-n fanning out N=4 internal calls each ≈ 3.5k
LLM calls).

Because the brief forbids editing core files, I will NOT modify `rex/eval_pass_at_k.py`.
Instead I write a thin task-namespaced runner `artifacts/run_full_pass_at_k.py` that:
  - imports `run_eval`, `print_report`, `floor_check` from the existing module,
  - calls `run_eval(model, conditions, per_family=None, seeds=...)` (the full set),
  - writes the result JSON + a checkpoint **inside A1/artifacts/** (not the shared dir),
  - supports `--conditions` and `--seeds` so a smaller, fast, fully-real run is possible
    if the full sweep is compute/time-blocked.

## Files to create
- `artifacts/run_full_pass_at_k.py` — task-namespaced full-set runner (imports core, no edits).
- `artifacts/full_pass_at_k_<model>.json` — the real result (full or honest partial).
- `artifacts/full_pass_at_k_<model>.json.partial` — crash-survival checkpoint.
- step files 01..10 + SUMMARY.md + result.json.

## Dependencies
- `agent.llm.call` (gateway model `glm-5p2`, HUD_API_KEY) — verified working (6.8 s/call).
- `rex.harness`, `rex.scoring` (deterministic judge), `rex.tree`, `rex.ablation`,
  `experiments/compute_pass_at_k.py` (estimator single-source-of-truth).

## Risks
- **Scale/time**: full 5-cond × 42 × 5 sweep is ~3.5k calls (~50+ min). Mitigation:
  checkpoint+resume already built into `run_eval`; my runner points the ckpt at my own
  dir. If the full 5-condition run can't finish in budget, deliver the two anchor
  conditions (`zero_shot`, `rex`) at full incident coverage + honest blocker for the rest.
- **API flakiness / rate limits**: `make_proposer` retries once; `work()` swallows dead
  calls into an errors list rather than aborting. I report `n_errors`.
- **Determinism of the JUDGE** (not the proposer): scoring is deterministic; only the LLM
  proposer is stochastic, which is the whole point of pass@k seeds.

## Success criteria
- A real `full_pass_at_k_*.json` covering **all 42 incidents** for >=1 model, >=1 condition,
  with non-trivial seeds, produced by the deterministic judge.
- `floor_check.floor_ok == true` (empty plan + trap both score < 0.8) across all 42.
- Per-family pass@1/2/5 + Wilson CIs + reward std reported.
- No shared core file edited; all new artifacts task-namespaced. Honest blocker if the
  full 5-condition sweep is truncated by time.
