# A8 — 05 Ouroboros (self-critique as 3 engineers)

## Engineer 1 — "the leak hunter"
**Problem found:** First implementation made Tier 2 require the company token PLUS
an extra shared *meaningful* token. But `launchdarkly_cold_cache` (cidg) vs
`launchdarkly_legacy_routing_cold_cache` (train) share only "cold"/"cache", both
on the STOP list → it was wrongly held out despite being the SAME company's SAME
incident. **Fix:** Tier 2 made HARD — same company present in training ⇒
contaminated, no extra-token requirement. After fix: launchdarkly, cloudflare,
aws, github, slack, circleci, datadog, incidentio scenarios all correctly excluded.
Verified: held-out dropped 18→15, and the company-named cidg incidents left in the
held set are only those whose company is NOT in training (facebook, knight, azure,
firefox, gke, kafka).

## Engineer 2 — "the over-engineering skeptic"
**Problem found:** The COMPANIES set hardcodes vendor tokens; if a future cidg
incident from a new vendor that *is* in training (e.g. "stripe") appears, it'd be
silently held out. **Assessment:** acceptable for this fixed corpus (32 incidents,
known vendors) but documented as a limitation in 09. Also flagged: Tier 3 soft flag
could confuse a reader into thinking class-overlap is ignored. **Fix:** manifest
`criteria` explicitly states Tier 3 is recorded-not-enforced + the `--strict-class`
switch is surfaced in the manifest (`strict_class_mode`).

## Engineer 3 — "the reproducibility auditor"
**Problem found:** If the builder and guard drift, a stale manifest could pass.
**Fix:** `assert_no_overlap.py` re-derives the training set from the raw jsonl
itself (does not trust the manifest's stored training_stats) and re-checks all
three signals. Added negative control proving it fails on a known contaminated id.
Also added `manifest_sha256` over the canonical content so any hand edit is
detectable. **Remaining nit:** sha is informational (guard doesn't verify it); for
this task scope that's fine — the guard's independent re-derivation is the real
defense.

## Final filtered spec
- Tier 2 is HARD (company-axis). ✅ implemented
- Tier 3 soft + `--strict-class`. ✅ implemented
- Independent guard re-derives training, negative control. ✅ implemented
- Manifest stratified by family, training_stats, sha256. ✅ implemented
- Documented limitation: COMPANIES list is corpus-specific. → 09_critique.
