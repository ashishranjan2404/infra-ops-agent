# C8 — 03 Improved Plan (post-grill)

## What changed vs 01
1. **Reframed the headline** (accepted AAAI + SMR R3). The deliverable is NOT "we beat
   89.7%." It is a **two-sided finding**: the 4th rule *is expressible in the existing
   feature set and IS effective* (held-out 89.7%→94.9%), **but the LLM search provably
   cannot discover it** because zero TRAIN examples activate `last_ready_node_op`.
2. **Added the train-signal count as the primary evidence** (accepted RLE). The
   artifact now reports `train_signal_for_rule4` — this is the load-bearing number.
3. **Added ALL-incident false-block delta** (accepted DevOps). The artifact + tests
   assert rule4 adds **no new false-blocks** vs baseline on TRAIN, HELDOUT, and ALL.
4. **Explicitly carved out the 2 unlearnable misses** (accepted PSRE/AAAI): the
   `cpu_saturation_leaf` trap_actions have no active feature, so 94.9% is the ceiling
   for the current `FEATURES` — matching the hand-written `is_safe` exactly.

## Critiques accepted
- AAAI's veto on "the search improved" framing — **accepted**. The search did not
  improve; the rule was human-injected. The report says so plainly.
- RLE's clean-isolation test (fix rules, inject one) — **accepted** as the method.
- DevOps's demand for measured (not asserted) false-block deltas — **accepted**.

## Critiques rejected (and why)
- PSRE's "even adding it to TRAIN might not generalize via the flaky operator" —
  **out of scope, not rejected on merit.** Re-running the haiku search is (a) costly,
  (b) non-deterministic, (c) blocked from editing core. C8 answers the *first*
  question (is the fix expressible+effective); re-running search is a follow-up.
  Documented as future work, not attempted, so we don't fabricate an LLM run.
- SMR's "this is a real positive property of data-rules" — **partially rejected.**
  It's true the data-rule design lets a human drop in the fix with no code change, and
  we note that, but we do NOT let it become the headline (AAAI wins the framing).

## Final method
Offline, deterministic, no LLM call. Load v2 rules → append rule4 (validated through
the synth's own `validate_ruleset`) → `confusion`/`train_score` on all splits → emit
JSON → pytest. Honest two-sided write-up.
