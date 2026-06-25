# 06 — Implementation

## Real artifacts created (all task-namespaced, NO shared-core edits)
- `artifacts/root_cause_accuracy.py` — the standalone metric + CLI (~230 lines).
- `artifacts/test_root_cause_accuracy.py` — 13 hermetic unit tests.
- `artifacts/run_output.txt` — captured human-readable run on real data.
- `artifacts/rca_result.json` — machine-readable `--json` run output.

## What it does
1. **Grounding in `rex/scoring.py`**: imports `rex.scoring._stems`, the exact
   deterministic tokenizer the shipped diagnosis judge uses, so category matching
   is phrasing-robust and hermetic (no LLM, no network). A guarded fallback keeps
   the module importable standalone.
2. **Grounding in scenario YAML**: `KIND_CATEGORY` mirrors
   `rex/harness.py:_KIND_CATEGORY`, mapping `root_cause.kind` from
   `scenarios/cidg/generated/*.yaml` to the 8 gold categories. The HUD export's
   `true_category` uses this same taxonomy, so gold labels are independent of the
   prediction path.
3. **`classify_root_cause(answer)`**: deterministic multi-class classifier over
   discriminative per-category keyword stems; ties / no-signal -> "unknown".
4. **`evaluate(records)`**: returns accuracy, per-category recall, confusion
   matrix, and the decoupling statistic (root-cause-correct vs incident-resolved).
5. **CLI**: `python3 .../root_cause_accuracy.py [--traj PATH] [--json]`.

## Proposed (NOT applied) integration into shared core
B7 must not edit shared files. The intended future wiring, documented here only:
- In `rex/eval_pass_at_k.py`, alongside the binary-pass aggregation, call
  `evaluate()` on the same episodes (passing each plan's `root_cause` as `answer`
  and the scenario's gold category) and report `root_cause_accuracy` as a separate
  column next to pass@k. This keeps diagnosis decoupled from the graded reward in
  `rex/scoring.py:score_plan`, which stays untouched.
This is left as a one-call addition; no patch is applied to any `rex/*.py`.

## Run command
```
python3 experiments/ralph_outputs/B7/artifacts/root_cause_accuracy.py \
    --traj opensre-traj/out/hud_trajectories.jsonl
```
