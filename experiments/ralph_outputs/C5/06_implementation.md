# C5 — 06 Implementation

## What I built (real artifacts, task-namespaced)
- `artifacts/gap_analysis.py` (159 lines) — runnable, deterministic. Imports the shared core
  read-only (`rex.harness_synth`); **edits no core file**. Loads the saved synthesized rule-set from
  `rex/runs/harness_synth.json`, runs both harnesses over all 140 labeled examples (10 incidents),
  emits the line-by-line diff.
- `artifacts/gap_report.json` (generated) — machine-readable diff per the 04 spec contract.

## How the comparison works
1. **The "lines":** I enumerated the 5 distinct clauses of `rex/harness.py:is_safe` with exact line
   refs (L1, L2a–L2d) as `HANDWRITTEN_CLAUSES`.
2. **Behavioral diff:** for every (tool,target) example I record `handwritten_block`, `synth_block`,
   `ground_truth_block`, and agreement. Disagreements split into *synth-misses* (false-allow gaps) and
   *synth-overblocks*.
3. **Clause→rule map:** each hand-written clause is matched to synth rules that reference the same
   hazard feature; the FULL synth-rule body (conditions + match_tools) is attached so the reader sees
   it's an approximation, not an equivalence (per Ouroboros Engineer A).
4. **Hazard gap:** per hazard, which incidents each harness blocks vs ground truth, with both
   `missed_by_synth` and `missed_by_handwritten` (fairness, Engineer B).

## Headline findings (real numbers)
- 140 examples, 10 incidents. Hand-written acc **0.871**, synth acc **0.864** — near-parity.
- Only **5 disagreements**: 3 where the hand-written harness blocks but synth lets through
  (false-allow gaps), 2 where synth over-blocks vs the human.
- **The single missing clause: `L2b_last_ready_node` (rex/harness.py:346-348)** — the synthesized
  rule-set has NO rule covering `last_ready_node_op`, so `drain_node`/`cordon_node` on the last Ready
  node (`singleton_node_notready`) is NOT blocked. This is the most severe gap (drains the only node →
  full outage).
- One more synth false-allow: `failover_service` on `cpu_saturation_leaf` (treats_forbidden_category) —
  the synth `treats_forbidden_category` rules don't include `failover_service` in their tool lists,
  so a forbidden-category treatment slips through that the general category clause catches.
- Synth over-blocks on `oom_kill` (`clear_cache`, `scale_deployment`) where its broad leak-active rule
  fires on tools the hand-written harness leaves alone.
- `trap_action` is missed by BOTH harnesses (no generic trap clause in either) — a **shared**
  limitation, not charged to synth.

## Proposed core change (NOT applied — written as documentation only)
To close the gap the synthesizer would need `last_ready_node` represented in BOTH train and held-out
(currently it is held-out-only → structurally unlearnable). That is a change to
`rex/harness_synth.py:TRAIN/HELDOUT`, a shared core file — per the brief I do NOT edit it; the proposal
is recorded here and in 09.
