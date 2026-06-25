# A7 — 01 Plan: Incident difficulty scoring

## Objective
Assign per-incident difficulty metadata — `expected_pass_rate` and
`trap_complexity` — to every scenario in `scenarios/cidg/generated/*.yaml`,
emitted as a **sidecar** artifact (JSON + CSV). No mutation of source YAMLs,
no edits to shared core `.py` files.

## Why this matters
The CIDG corpus mixes trivial synthetic incidents (single service, single-step
fix) with hard real-world postmortems (multi-node cascades, buried evidence,
loud-but-wrong alerts). Without a difficulty label the eval/curriculum layer
treats them uniformly, which (a) makes pass@k numbers uninterpretable and
(b) blocks curriculum ordering. A transparent difficulty score unlocks
stratified reporting and curriculum sampling.

## Approach
Heuristic, model-agnostic scoring from structural signals already present in
each YAML — no LLM, no live runs, fully deterministic:
- `trap_complexity` ← topology size, edge fan-out, `assertions.cascades`,
  `assertions.loudest_alert_not_cause`, `root_cause.hidden`, smoking-gun
  `buried_under` depth, hysteresis, monitoring degradation, trap-action count,
  severity.
- `expected_pass_rate` ← base prior (clean incident) minus penalties driven
  mainly by trap_complexity, plus fix-step count, flap/jitter dynamics, and
  number of simultaneous SLOs.
- `difficulty_bucket` ← easy/medium/hard thresholds on expected_pass_rate.

## Files to create
- `experiments/ralph_outputs/A7/artifacts/score_difficulty.py` (new script)
- `…/artifacts/difficulty_scores.json` + `.csv` (generated output)
- the 10 step docs + SUMMARY.md + result.json

## Dependencies
Python 3.13 stdlib + `pyyaml` (already in requirements). No network.

## Risks
- Heuristic weights are unvalidated against real pass rates (no labelled runs
  in the corpus). Mitigate: keep every weight documented + auditable; ship a
  per-component breakdown so the prior can be recalibrated later.
- Corpus is low-variance on some fields (severity always 0.7, flap always 0.05)
  → those terms barely discriminate. Acceptable; the discriminating signals
  (cascades, hidden, buried_under, topology) carry the spread.

## Success criteria
1. Script runs clean on all real YAMLs (33) and emits valid JSON + CSV.
2. Both metrics in [0,1]; meaningful spread (not all-same).
3. Ranking is face-valid: synthetic single-node incidents land "easy",
   multi-node cascading postmortems land "hard".
4. Zero mutation of source YAMLs; zero edits to core `.py`.
