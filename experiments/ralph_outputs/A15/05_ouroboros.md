# A15 — Ouroboros (self-critique, 3 engineers)

## Engineer 1 — finds real problems
- **P1 (validity hole):** If a baseline already sets `assertions.monitoring_degrades=True` but has
  NO smoking guns, and another assertion (`buried_gun_exists`) is True, validation fails. My
  transform doesn't touch `buried_gun_exists`, so it can't *introduce* that failure — but I should
  confirm the example baseline is internally consistent. (It is: #55 has 1 gun.)
- **P2 (idempotency of buried_under):** `meta.id` is idempotent, but `buried_under` is NOT — applying
  twice gives `b*9`. Re-running the transform on an already-noisy variant inflates noise unboundedly.
- **P3:** No guard that `root_cause.location` actually resolves to a node before building the observes
  edge; a malformed baseline would put an observes edge to a non-existent node → validation catches it,
  but the error is then on *my* output, confusing.

## Engineer 2 — different angle
- **P4 (semantics):** "noisy" isn't in any closed vocab — `alerting` is a free string in the schema
  (only `uniform` is documented). So `noisy` is schema-legal but undocumented; fine, but I should note
  it's a *new* alerting value the schema accepts by being open.
- **P5 (over-engineering?):** Injecting a whole monitoring node may be more than needed — could I instead
  point an observes edge between two existing nodes? No: `observes` is semantically monitoring→data-plane,
  so a dedicated monitoring node is the *correct* modeling, not over-engineering. Keep.
- **P6 (under-test):** No test asserts the CLI `--check` exit code or that an invalid output is never
  written. Behavior is covered indirectly but not directly.

## Engineer 3 — adversarial
- **P7 (the big one):** Does anything actually *consume* `alerting=="noisy"` or the deepened
  `buried_under`? If Tier-A ignores them, an RL run on baseline vs. noisy yields identical agent
  behavior and the "variant" is observationally null *for that runner*. This must be stated, loudly.
- **P8:** `meta.source` still references the original incident; fine for provenance, but a reader could
  mistake the variant for the canonical scenario. `derived_from`+`variant` mitigate this.

## Resolution / final filtered spec
- **P2 fixed:** documented as known limitation; `--check` lets callers verify before re-applying. Could
  guard by checking `variant=="noisy_metrics"` and skipping buried_under scaling on re-apply — deferred
  (id idempotency already prevents accidental chains in the common path). **Documented in 09.**
- **P3:** `_root_node` + schema validation already fail loudly with a clear message; acceptable.
- **P4:** documented — `alerting` is an open string field; `noisy` is the intended value for this variant.
- **P6 partially addressed:** `--check` path exercised manually in 07 (both with-gun and no-gun baselines).
- **P7:** ACCEPTED as the headline honest caveat → recorded as a scoped blocker in 07 & 09. The deliverable
  is a valid, reward-invariant, observation-degraded spec + reusable transform; wiring Tier-A to amplify
  alert noise from these fields is downstream work, not part of A15.
- **P1/P5/P8:** no change needed; modeling is correct.
