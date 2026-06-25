# A11 — 09 Critique (honest)

## What a reviewer attacks
1. **Difficulty/transfer confound (the strongest attack).** All three A-variants
   are easy leaves and all three B-variants are hard buried cascades, so
   "direction of transfer" is perfectly correlated with "difficulty" *across*
   pairs. A model that solves all A and fails all B may simply be unable to do
   buried-root localization — that is a capability gap, not a transfer failure.
   *Mitigation shipped:* the manifest + per-YAML `cascades/loudest_alert_not_cause/
   buried_gun_exists` booleans let an analyst run the test in BOTH directions
   (train-on-cascade → test-on-leaf isolates pure transfer). *Residual weakness:*
   we did not ship a difficulty-matched pair, so the confound is exposed but not
   eliminated.

2. **Only 3 pairs.** Too few for a statistically meaningful transfer-gap estimate.
   This is a seed set, not a benchmark. Honest: it demonstrates the *construction
   method* (and the generator makes scaling cheap) but the number itself proves
   nothing.

3. **"Same root cause" is defined operationally, not causally.** We equate root
   cause with `failure_class + fix tool`. Two scenarios with the same fix could
   still differ in the *reasoning path* needed to reach it (a leaf needs no
   upstream tracing; a cascade does). So the pairs test "same fix transfers across
   symptom" more than "same mechanism." Defensible, but a purist would object.

4. **No execution evidence.** I validated YAML/schema/invariants but did not run a
   policy through the sim on these scenarios, so I have not empirically confirmed
   `fix_resolves` actually holds in-sim for the new topologies. The assertion is
   declared, not measured. This is the biggest honesty gap; a follow-up should run
   `rex/eval_pass_at_k.py` (or the harness) on the canonical fix to confirm the
   SLO clears.

## What's missing / follow-ups
- A 4th and 5th pair that flip the difficulty direction (cascade-A / leaf-B) to
  decorrelate difficulty from transfer direction.
- An actual in-sim smoke test that the canonical fix resolves each new scenario.
- Registry integration (deferred to avoid editing the shared `registry.json`
  under parallel execution).

## Net
Real, valid, reusable artifacts that correctly implement "same root cause /
different symptom" pairs and make the difficulty axis explicit. The honest limits
are scale (3 pairs), an exposed-but-unremoved difficulty confound, and no in-sim
fix-resolves verification.
