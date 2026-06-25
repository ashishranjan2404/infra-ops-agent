# A8 — 01 Plan

## Objective
Create a held-out test set of SRE incidents that NO training data touches
(strict novelty), so eval numbers reported on it cannot be inflated by
memorization / train-test contamination.

## Approach
1. Enumerate the candidate incident pool: `scenarios/cidg/generated/registry.json`
   (32 incidents across `simple`, `cascade`, `novel` families).
2. Enumerate every identifier the training data touches:
   - `opensre-traj/out/trajectories.jsonl` (synthetic SFT/RFT trajectories)
   - `opensre-traj/out/hud_trajectories.jsonl` (HUD rollout traces)
   Extract distinct `incident` ids and `scenario_id`s.
3. Define an auditable, tiered **novelty criterion** and classify each candidate
   as held-out or contaminated.
4. Emit a **manifest** (JSON) + **flat split** (CSV) listing exactly which
   incident ids are strictly held out, with per-incident reasons.
5. Ship a **standalone assertion script** that re-derives the training set and
   fails (exit 1) on any overlap. Run it; add a negative-control test.

## Files to create (all under experiments/ralph_outputs/A8/)
- `artifacts/build_heldout_split.py` — builder + classifier
- `artifacts/assert_no_overlap.py` — independent guard
- `artifacts/heldout_manifest.json`, `artifacts/heldout_split.csv` — outputs

## Files I will NOT modify
Shared core: `rex/*.py`, `sim/*.py`, `agent/*.py`, `experiments/*.py`,
`scenarios/cidg/generated/*` (read-only), training jsonl (read-only).

## Dependencies
`python3`, `pyyaml` (already a rex dep) to parse scenario YAML.

## Risks
- Naive string match under-counts contamination (paraphrased / same-source
  incidents). Mitigation: tiered criterion incl. a company/vendor identity axis.
- Over-aggressive token matching nukes legitimately novel incidents that merely
  share a generic infra word ("cache", "cert"). Mitigation: stop-list of generic
  tokens; require token *pairs*, not single tokens, for the n-gram tier.

## Success criteria
- Manifest lists the held-out incident ids + the exact novelty criteria.
- `assert_no_overlap.py` exits 0 on the held-out set, exits 1 when a known
  contaminated id is injected (negative control).
- No shared core file edited.
