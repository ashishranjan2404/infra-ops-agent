# C5 — 05 Ouroboros (self-critique as 3 different engineers)

## Engineer A — correctness auditor
**Problem found:** The clause→rule map keys on a single feature per hazard. The synth rule-set has
*compound* rules (e.g. rule 1: `match_tools=[clear_cache,restart_pod,...] AND leak_active==True`). My
map will mark `leak_restart` as "covered" because `leak_active` appears — but that rule fires on
`leak_active` regardless of whether the tool is a restart, AND it has the WRONG tool list. So
"represented_in_synth=True" overstates fidelity: the synth rule is a *coarser, different* predicate, not
a faithful port of L2a. **Fix:** keep the boolean coverage flag but ALSO surface the actual synth rule
conditions in the map so a reader sees it is an approximation, not an equivalence. (Implemented:
`synth_rules_covering` includes full conditions + match_tools + reason.)

## Engineer B — fairness / methodology
**Problem found:** Counting `trap_action` against the synth harness is unfair — the hand-written
`is_safe` has NO generic trap clause either (it only catches the gcp trap via the category block). If I
list trap_action under "synth gaps" without noting hand-written misses it equally, I manufacture a fake
win for the baseline. **Fix:** `hazard_gap` reports BOTH `missed_by_synth` and `missed_by_handwritten`;
the prose in 08/09 explicitly labels trap_action a *shared* limitation. Verified by T4.

## Engineer C — scope / over-engineering
**Problem found:** Am I over-building? A 200-line analysis to diff a 10-rule set against 5 clauses may
be heavier than needed. Counter: the per-example behavioral diff over 140 examples is the load-bearing
evidence (the headline 3 false-allows fall out of it), and it's deterministic and cheap. NOT over-built.
**Under-engineering risk:** I don't quantify *operational impact* (a missed last-ready-node = full
outage vs a missed forbidden-category = treating a non-cause). **Fix:** add impact framing in 09 (not
code) — last_ready_node is the highest-severity miss; flag it explicitly.

## Final filtered spec
- Keep behavioral diff + false-allow headline + clause map with full synth-rule bodies (A).
- Report missed_by_synth AND missed_by_handwritten per hazard; label trap_action shared (B).
- Add severity framing for the missing last_ready_node clause in prose (C). No core-file edits.
