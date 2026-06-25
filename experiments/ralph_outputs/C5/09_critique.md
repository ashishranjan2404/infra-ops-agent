# C5 — 09 Critique (honest)

## What a reviewer will attack
- **Small N.** 10 incidents / 140 examples. The "missing clause" finding rests on a SINGLE held-out
  incident (`singleton_node_notready`) for the `last_ready_node` hazard. One incident is thin evidence;
  it's enough to *demonstrate* the gap but not to quantify its frequency.
- **The gap is structurally guaranteed, not surprising.** `last_ready_node` appears ONLY in the
  held-out split (per `rex/harness_synth.py:TRAIN/HELDOUT` + the synthesis run's own hazard-coverage
  report: `leak_restart` train-only, `last_ready_node` held-out-only). The synthesizer was never given
  a labeled example of that hazard, so it *could not* learn it. So "synth misses L2b" is partly an
  indictment of the SPLIT design, not the search. I report it as a real guardrail gap AND name the
  root cause honestly (the AAAI-reviewer persona's point in 02).
- **Clause→rule mapping is approximate.** A clause is marked "represented" if any synth rule references
  its hazard feature — but the synth rules are coarser/compound (e.g. a `leak_active` rule fires on a
  4-tool list, not faithfully on restart_* only). "Represented" ≠ "equivalent." I mitigated by
  attaching the full synth-rule bodies, but the boolean flag still overstates fidelity if read alone.
- **`treats_forbidden_category` is only partially covered by synth.** The synth rule-set expresses this
  hazard as several per-tool-list rules instead of ONE general no-match_tools rule (which the schema
  explicitly recommends). That's why `failover_service` slips through. So even the "OK" clauses are
  brittle ports — the comparison is parity-on-average but not invariant-for-invariant.

## What's weak / blocked
- I did NOT re-run the synthesis (would need the haiku API + budget; also it's a shared-core change).
  I compared against the *saved* rule-set, which is the correct scope for a comparison task but means
  the finding is conditional on that one run's output.
- No operational-severity weighting in the numbers — `last_ready_node` (full outage) and
  `treats_forbidden_category` (treats a non-cause) are counted equally as "1 false-allow" each.
  I flag severity in prose only.

## Honest bottom line
The synthesized harness reaches near-parity accuracy (0.864 vs 0.871) but is **missing one safety
invariant the human encodes (last-ready-node) and ports two others brittlely (per-tool forbidden-
category, broad leak-active)**. The single missing invariant is the highest-severity gap and is
traceable to the train/held-out split — a real, defensible, negative-leaning finding, not a win
manufactured for the baseline.
