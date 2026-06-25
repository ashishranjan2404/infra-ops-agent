# A15 — Honest Critique

## What a reviewer will attack
1. **"Inert fields."** The strongest attack: `alerting` and `buried_under` are not read by Tier-A
   `propagate()`, so on the fast sim alone the noisy variant behaves identically to the baseline.
   Mitigation: the deliverable is explicitly scoped to a *schema-valid, reward-invariant,
   observation-degraded spec + reusable transform*; the engine-consumption wiring is documented as
   downstream (and would require editing shared core, which the brief forbids). Still, until that
   wiring lands, the *behavioral* value of the variant is latent, not demonstrated. This is the
   biggest honest weakness.
2. **buried_under not idempotent.** Re-applying the transform to an already-noisy variant multiplies
   `buried_under` again (b→3b→9b). The `meta.id` suffix is idempotent, but noise scaling is not.
   A caller who re-runs blindly inflates noise. Documented; a `variant=="noisy_metrics"` guard was
   deferred. Low severity (the common path runs once on a baseline).
3. **Single example.** Only one variant YAML is shipped (#55). The transform is validated on two
   baselines via `--check`, but only one is materialized. A reviewer wanting a full noisy *suite*
   would want all ~33 scenarios transformed — trivial to batch, not done here to keep scope focused.
4. **"noisy" is an undocumented alerting value.** `alerting` is an open string; `uniform` is the only
   documented value. `noisy` is schema-legal but conventions aren't enforced — a typo elsewhere
   wouldn't be caught.
5. **Added monitoring node is a topology change.** Defensible (observes = monitoring→data-plane is the
   correct modeling), but it does mean the noisy variant has one more node than its baseline, so
   "identical topology" is false; "identical *physics-bearing* topology + identical reward" is the
   accurate claim.

## What's weak / missing
- No measured agent A/B (blocked by inert fields — honest, not faked).
- No CLI exit-code test (covered manually, not in pytest).
- No batch mode to emit the full noisy suite.

## What's solid
- Pure, tested, cwd-independent transform that round-trips through the real validator.
- Reward invariance enforced and tested (root_cause/canonical_fix byte-identical).
- Zero edits to shared core or source scenarios; fully reproducible from baselines.
