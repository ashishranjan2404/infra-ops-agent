# H5 — 05 Ouroboros (self-critique as 3 different engineers)

## Engineer A — Frontend/robustness
**Problems found:**
- `file://` fetch will fail silently and the user sees an empty page. → FIXED: loud error
  box with explicit serve hint + file-picker fallback wired before first render.
- No schema validation: a malformed manifest would throw deep in `render()` with a cryptic
  message. → FIXED: `validate()` checks schema, candidates array, and gate up front.
- Sorting could `NaN`-compare when `pass_at_2/5` are null. → FIXED: coalesce `??-1` in the
  comparator so nulls sort last deterministically.

## Engineer B — Stats/methodology
**Problems found:**
- Lift computed vs a *global* baseline would be wrong across models. → CONFIRMED FIXED:
  each loader computes baseline from that model's own `zero_shot` row.
- The 95% CIs are taken as-given from A1/A2; the dashboard must not re-derive or it'll
  disagree with the source. → KEPT: dashboard only renders precomputed CIs, never recomputes.
- A2's `rex.cascade` pass@1 is 0.68 with CI_lo 0.54 — note the *overall* rex row still
  promotes (0.893, CI_lo 0.834), but per-family the dashboard honestly shows cascade is the
  weak family. This is surfaced, not hidden. Good (anti-cherry-pick).

## Engineer C — Maintainability/over-engineering
**Problems found:**
- Two near-duplicate loaders (`load_a1`/`load_a2`) — mild duplication, but justified
  because the source schemas genuinely differ (`p1`/`ci` vs `pass@1`/`ci95`). A single
  generic loader would need a key-map config that is more code than the duplication. KEPT.
- Gate thresholds are hardcoded constants. Acceptable for v1; documented in the manifest's
  `gate` block so the HTML reads them dynamically rather than re-hardcoding. The yellow
  threshold tick is driven by `gate.promote_p1`, so changing the constant reflows the UI.
- No automated browser test, only a Node DOM shim. Accepted limitation — the shim exercises
  the real `loadManifest`/`render` path and asserts counts; full visual is a manual glance.

## Final filtered spec
No schema changes needed; all three rounds resolved into fixes already in the design:
loud-fail fetch, up-front validation, null-safe sort, per-model baseline, render-only CIs,
gate-driven threshold tick. Duplication and hardcoded gate retained with rationale.
