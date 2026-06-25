# C3 — 06 Implementation

## What I built
`experiments/ralph_outputs/C3/artifacts/run_novel_synth.py` — a task-namespaced runner
that performs harness synthesis on **only novel incidents** (the C3 generalization test).
It **imports and never edits** the shared core `rex/harness_synth.py` (and `rex/tree.py`,
`rex/harness.py`). Specifically it reuses, verbatim:
- `labeled_examples`, `features`, `ground_truth` — the labeled-example pipeline;
- `propose_ruleset` — the LLM mutation operator (data-only; no exec);
- `train_score`, `confusion`, `confusion_pred`, `handwritten_pred` — reward + scoring;
- `hazard_coverage` — scope table;
- `thompson_search` — the Thompson-tree search.

## How it differs from the shared default
| | `rex/harness_synth.py` default | C3 runner |
|---|---|---|
| TRAIN | 7 mixed (seen vendors incl. cloudflare/aws) | 10 **A8-certified-novel** |
| HELDOUT | 3 mixed | 5 **A8-certified-novel** |
| novelty | informal | enforced ⊆ `A8.held_out` at runtime |
| model | `claude-haiku-4-5` | `$C3_MODEL` (ran `gpt-5.5`, Anthropic credits out) |

## Provenance / safety enforced in code
- `_load_novel_universe()` reads `A8/artifacts/heldout_manifest.json → held_out` (15 ids).
- `assert (TRAIN ∪ HELDOUT) ⊆ novel` and `assert TRAIN ∩ HELDOUT = ∅`.
- Both `propose` and `evaluate` closures take **only** `train_ex`; held-out labels are
  touched solely in the final scoring pass after `best` is frozen.

## Model swap (documented, not hidden)
Default operator `claude-haiku-4-5` returns HTTP 400 (Anthropic credits exhausted in
this env). I ran with the HUD gateway model `gpt-5.5` (verified live). The swap is sound:
the operator only emits a JSON rule list; output is validated by `validate_ruleset` and
interpreted by trusted code — the model is a proposal source, not executed. Model+budget
are recorded in stdout and in `novel_synth_result.json`.

## Artifacts produced (real)
- `artifacts/run_novel_synth.py` — the runner (≈170 LOC, runnable).
- `artifacts/novel_synth_result.json` — emitted metrics + rules + leakage proof.

## NOT a core change
No file under `rex/`, `sim/`, `agent/`, `experiments/*.py`, `scenarios/`, or A8's dir
was modified. (Note: the runner *temporarily* rebinds the module-level `hs.MODEL` inside
its own process for the duration of `_propose` and restores it — an in-memory override,
not a source edit.)
