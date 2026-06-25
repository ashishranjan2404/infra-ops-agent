# B4 — Verification against success criteria

| Success criterion (from 01_plan) | Met? | Evidence |
|---|---|---|
| Every `*.yaml` in generated/ gets exactly one type label (51/51) | YES | T1: 51 in → 51 unique rows; T2 all valid |
| 3 SEPARATE pass@k tables, one per type | YES | `stratified_simple.md`, `stratified_cascade.md`, `stratified_novel.md` each render independently |
| Tables built from REAL result numbers, not placeholders | YES | T8 parity: 105/105 cells equal A1's published `by_family`; deepseek rows from A2 |
| Reuse A7 difficulty + A8 novelty sidecars | YES | classifier loads `difficulty_scores.csv` (difficulty col) and `heldout_split.csv` (family); registry+A8 cover the 32 labelled |
| Classifier counts cross-check registry / A8 | YES | T3=0 mismatch, T4 counts simple=8/cascade=14/novel=10 match registry & A8 |
| Script runs clean, re-runnable | YES | both scripts run to completion; glob-discovery, stdlib+pyyaml only |
| Did NOT edit shared core files | YES | `git status` shows only new files under B4/artifacts (see below) |

## Outputs are real, not placeholder
- `incident_types.csv/json`: 51 concrete rows with id, type, source_tier, difficulty.
- `stratified_*.md`: each has 10 data rows of actual pass@1/2/5 + Wilson CIs from glm-5p2 (A1)
  and deepseek-v4-pro (A2) runs. Sample (novel, glm-5p2, rex): pass@1 = 1.000 [0.886,1.000];
  (novel, glm-5p2, zero_shot): 0.167 [0.073,0.336].
- `stratified_pass_at_k.json`: machine-readable rows + `consistency_mismatches: []`.

## No-shared-edit proof
The only paths written are under `experiments/ralph_outputs/B4/`. `rex/*.py`, `sim/*.py`,
`registry.json`, A1/A2/A7/A8 directories, and `ralph_status.json` were opened read-only.

## Honest gaps (carried to 09)
- 19 of 51 incidents are classified but have NO eval results (not in registry → harness never
  ran them). Tables disclose these per type. Their pass@k is therefore unmeasured, not zero.
- `rex` cells show reward_std=0 (saturated) — real but a trainability concern, not a B4 bug.
