# I6 — 01 Plan: Failure-mode taxonomy of 0-reward rollouts

## Objective
Categorize every failed / 0-reward (or low-reward, non-clean-win) rollout in the
project's existing rollout data into interpretable **failure-mode buckets**
(trap-taken, wrong-root-cause, no-fix, not-resolved, timeout/empty, etc.) using the
deterministic signals already produced by `rex/scoring.py`, then report the
distribution per scenario, per failure type, and per data source.

## What "failed" means here (graded reward caveat)
`rex/scoring.py` is GRADED, not binary: `score = 0.30·diag + 0.25·fix + 0.45·resolved
− 0.60·trap`, clipped to [0,1]. Pure 0.0 rollouts are rare because partial credit is
common. So the analysis treats a rollout as **failed** if it is NOT a *clean win*:
i.e. `score < 1.0` OR any non-empty `failed_checks`. We additionally flag the strict
subset `score == 0.0`. Each failed rollout is labeled with one PRIMARY bucket plus any
secondary tags, derived from `failed_checks` + score components.

## Data sources to mine (real, on disk)
1. `rex/runs/diagnostic_probe_*.jsonl` — 12 rollouts, each already has
   `score`, `resolved`, `diagnosis_correct`, `failed_checks`. Direct ingest.
2. `rex/runs/hud/*.jsonl` — 35 HUD trace files. The `rex.score_plan` /
   `rex.failed_checks` spans carry the full `{plan, scenario, sim_result}` request
   payload (52 each). The score/checks RESPONSE is not recorded, so we **re-derive**
   them deterministically by replaying `rex.scoring.score_plan` + `failed_checks`
   over the captured tuple (a lightweight `_Scenario` shim reads the flattened
   scenario fields the scorer needs). This is the core trick: real captured episodes,
   re-scored hermetically.
3. `rex/runs/frontier.json`, `harness_synth.json` curriculum cells — per-cell baseline
   vs rex scores (aggregate, no per-episode checks) — used as a cross-check on the
   distribution, not as primary per-rollout records.

## Failure buckets (from rex/scoring.py signals)
- `trap_taken`        — `trap_action` in failed_checks (forbidden/destructive action)
- `wrong_root_cause`  — `root_cause` in failed_checks (diagnosis judged WRONG)
- `no_fix`            — `correct_fix_missing` (no/partial remediation on the fault node)
- `not_resolved`      — `not_resolved` (SLO still breaching)
- `empty_plan`        — plan has no actions at all (escalate/abstain or give-up)
- `clean_win`         — no failed_checks and score==1.0 (excluded from failure set)
Primary bucket precedence: trap_taken > wrong_root_cause > no_fix > not_resolved.
(A trap is the most safety-critical, so it dominates the label.)

## Files to create (task-namespaced, no shared edits)
- `artifacts/failure_taxonomy.py` — the analysis script (imports rex.scoring read-only).
- `artifacts/failure_report.json` — machine-readable distribution.
- `artifacts/failure_report.md` — human-readable report.
- `artifacts/test_failure_taxonomy.py` — pytest over synthetic + a real-data smoke test.

## Dependencies / risks
- Risk: HUD traces don't record the score response → MITIGATED by re-scoring from the
  captured request payload (deterministic judge, no network).
- Risk: scenario shim mismatch → MITIGATED by reading the exact attributes `score_plan`
  touches and unit-testing equality vs probe-file ground truth where overlap exists.
- Risk: small N (≈12 probe + ≈52 hud unique episodes) → report honestly, no extrapolation.

## Success criteria
Script runs on real data, emits a per-bucket distribution, agrees with the probe files'
pre-computed `failed_checks` on overlapping rows, tests pass, no shared core file edited.
