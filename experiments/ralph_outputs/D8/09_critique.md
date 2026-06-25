# D8 — 09 Critique (honest)

## The headline blocker
The entire scientific payload of Claim 2 — "Fireball SFT transfers to cascade
SRE incidents" — is **unverified and unverifiable in D8** because the real
FIREBALL corpus is not in the repo (pending from Wenji). What I delivered is the
ingest + config + test scaffold, not evidence. A reviewer is right to say D8
produces zero new support for Claim 2's truth. That is the honest state.

## Where a reviewer attacks the artifact itself
1. **The transfer mechanism is assumed, not demonstrated.** The system prompt
   ("this mirrors diagnosing...") bakes in the very hypothesis the eval should
   test. If structural transfer is illusory, the adapter still "works" but trains
   a worse model. The adapter cannot validate its own premise.
2. **Reward design is a judgment call.** Down-weighting no-state-change turns to
   0.8 could be exactly wrong for SRE, where "probe returns nothing" is a crucial
   transition. I argued it's a mild quality signal, but it's defensible-not-proven.
3. **State equality is naive.** `before_state != after_state` is a raw structural
   compare; int-vs-float HP or key reordering in the real dump could mislabel
   `state_changed`. Hardening item: normalize states before compare.
4. **Discarded signal.** Real FIREBALL state is far richer (positions, conditions,
   spell slots, initiative) than `_fmt_state` renders. We may be throwing away the
   most transferable structure. v1 keeps it simple; flagged for v2.
5. **Fixture is trivially small (7 records).** It proves the adapter mechanically
   but says nothing about real-data scale, schema drift, or distribution.
6. **Single-run heritage.** Even when the data lands, Claim 2 currently rests on
   one of Wenji's runs. Without multi-seed + CI on a *pre-registered* cascade/simple
   split, the asymmetry could be noise. The config records this bar but D8 does
   not meet it.
7. **Adapter/config contract gap.** The `min_examples_for_real_run` guard lives in
   the config, not enforced by the adapter — a careless caller could train on the
   fixture if the training layer ignores the guard. I treated the adapter as a pure
   transform deliberately, but it's a seam.

## What's missing
- The real corpus (the blocker).
- A trained Fireball model and any transfer numbers.
- A pre-registered, defensible cascade-vs-simple incident taxonomy (the eval
  references `incident_class` but the labeling rule isn't pinned down here).
- State normalization + richer state rendering for real data.

## Honest verdict
Solid, tested scaffold; correct refusal to fabricate; the science is entirely
ahead of us and gated on data we don't have. Status: deliverable completed,
Claim-2 evidence blocked.
