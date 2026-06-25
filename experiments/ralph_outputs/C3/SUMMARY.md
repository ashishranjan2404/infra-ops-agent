# C3 — SUMMARY

## Task
Run harness synthesis (`rex/harness_synth.py`) on **only novel incidents** and report
generalization of the synthesized safety rules.

## What was done
Built a task-namespaced runner `artifacts/run_novel_synth.py` that **imports (never
edits)** the shared synthesis machinery and re-runs Thompson-tree rule synthesis over a
TRAIN(10)/HELDOUT(5) split drawn **entirely from the A8 strict-novel set** (15 cidg
incidents A8 certified as zero-overlap with the policy's training trajectories). The
split is enforced at runtime to be a subset of A8's certified-novel ids and
TRAIN-intersect-HELDOUT = empty. The LLM mutation operator only emits JSON rule data
(never executed); a trusted interpreter applies rules over 6 known features. Ran with
`gpt-5.5` (HUD gateway) because the default `claude-haiku-4-5` is out of Anthropic
credits (HTTP 400).

## Result (generalization on NOVEL incidents)
| harness | TRAIN acc | TRAIN FA% | HELDOUT acc | HELDOUT FA% |
|---|---|---|---|---|
| seed (empty) | 0.522 | 1.00 | 0.500 | 1.00 |
| **synthesized (novel-train)** | **0.978** | **0.016** | **0.941** | **0.059** |
| hand-written `is_safe` | 0.970 | 0.062 | 0.956 | 0.088 |

Synthesis autonomously recovered the general rule `treats_forbidden_category==True` from
novel labels (no incident ids) and **transferred it to 5 held-out novel incidents at
94.1% accuracy / 5.9% false-allow - competitive with the human harness**, stable across
2 runs.

## Honest limits
- Held-out mistakes: **2 false-allows** (`media_oom_leak` leak-restart - hazard unseen in
  TRAIN, out-of-scope) and **2 false-blocks** (an over-general `scale_deployment` rule the
  operator added). The gap to 100% is **structural**: `trap_action`/`leak_restart` aren't
  expressible in the 6-feature rule language. Single model/budget (no sweep).

## Artifacts
- `artifacts/run_novel_synth.py`
- `artifacts/novel_synth_result.json`

## Core files modified: NONE (only `experiments/ralph_outputs/C3/` added).
