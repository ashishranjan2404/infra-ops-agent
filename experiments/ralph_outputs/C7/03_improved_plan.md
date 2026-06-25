# C7 — Improved Plan (post-grill)

## What changed vs 01_plan.md

### Accepted critiques
- **(AAAI/PSRE) Full confusion, not just accuracy.** The artifact now dumps tp/tn/false_allow/
  false_block per harness per family, plus false-allow rate. Accuracy is reported but never alone.
- **(PSRE) False-allow is the safety-critical metric.** On cascades, a single false-allow can herd
  the incident worse. We surface false-allow count + rate prominently and list the actual
  false-allowed (incident, tool, hazard) tuples.
- **(SMR↔PSRE) Reframe the baseline.** The hand-written `is_safe` is quoted as an **oracle /
  upper bound**, explicitly NOT "generalization" — it loads each incident's `forbidden_categories`
  from spec, so its cascade accuracy is high by construction. The synthesized harness's gap is
  reported *relative to* this oracle, with that caveat stated.
- **(RLE↔AAAI) Auditability.** Pin `MODEL` + `BUDGET` + `seed=0`; SAVE the synthesized rule-set and
  node scores to `transfer_result.json` so the whole evaluation replays deterministically offline
  via `is_safe_synth` even if haiku drifts.
- **(DOL) Empty-ruleset = blocker, not failure.** If the best ruleset is empty (synthesis didn't
  improve on seed / LLM unavailable), we flag `synthesis_ran=false` and report a BLOCKER rather
  than claiming a transfer collapse.
- **(DOL) No core edits.** Standalone `artifacts/transfer_simple_to_cascade.py` imports from
  `rex.harness_synth` and `rex.harness`; touches nothing shared.

### Rejected critiques (with why)
- **(PSRE, R2) "Drop the hand-written baseline entirely."** REJECTED. It's the only available
  ceiling that proves the task is solvable; removing it leaves the synthesized number context-free.
  Compromise kept: relabel it an oracle, don't call it generalization.
- **(AAAI, R2) "LLM stochasticity makes it unscientific."** REJECTED as framed. Saving the
  rule-set makes the *claim* replayable; the interpreter is deterministic. We accept the mitigation
  (save artifacts) without accepting the conclusion.

## Final transfer-gap definition
For harness H: `gap(H) = accuracy_train(H) - accuracy_heldout(H)` where train=simple, heldout=cascade.
Headline:
- `gap(synthesized)` = cross-type transfer gap of the searched harness.
- `gap(hand-written)` = oracle gap (irreducible distribution shift; ~0 expected).
- `synthesis_transfer_cost = gap(synthesized) - gap(hand-written)`.
Plus the safety headline: cascade false-allow rate of the synthesized harness.

## Run config
MODEL=`claude-haiku-4-5`, BUDGET=8 (matches core default; ~8 LLM calls, within 15-min cap),
seed=0, stop_at=1.0. TRAIN=all 12 simple, HELDOUT=all 20 cascade.
