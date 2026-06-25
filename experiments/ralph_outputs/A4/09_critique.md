# A4 — Honest Critique

## Where a reviewer attacks
- **"This is an email, not research."** True at the surface. The defense is the
  schema + validator: a real, tested data contract that de-risks ingestion and
  proves we did homework. But the headline task (get incidents) is **not
  achieved** — no data was obtained, and an automated worker structurally cannot
  obtain it. The honest status is "package ready, outcome pending a human + a
  reply."
- **"You can't verify the contact."** Correct. Research confirmed Snorkel's
  *channels* (partner form, contact page, LinkedIn) and a *public persona*
  (Armin Parchami) but **no direct email**. We refuse to fabricate one, so the
  email routes through a form/warm intro — lower hit-rate than a targeted send.
  Flagged, not hidden.
- **"Even if they say yes, the data is still constructed."** The strongest
  critique (REV's). Snorkel's model is expert-authored/curated data. Partner
  records would **not** close the `INCIDENT_DATASET.md` "0 fully real raw
  incidents" gap. They close the narrower *self-authoring/contamination* gap. The
  brief and checklist say this explicitly; if a future reader over-claims, that's
  a process failure, not a representation in these artifacts.

## What's weak / missing
- **No converter.** The schema is validated but the `partner_record → scenario
  YAML` step is only specified, not built (deliberate, parallel-safety). Until it
  exists, "drops straight into the pipeline" is a claim, not a demonstrated fact —
  though the field-mapping test (T5) makes it low-risk.
- **Reward-semantics assumed, not run.** I assert the verifier grades
  trap_actions/canonical_fix/slo; I did not run a real episode through
  `rex/scoring.py` with an ingested record (would require the converter + sim
  wiring). So "trainable" is argued, not proven end-to-end.
- **Tool vocabulary is partial.** `x-recommended-tools` is hand-derived from the
  catalog; the real simulator tool registry (in `sim/`) wasn't enumerated, so the
  warn-list may be incomplete. Acceptable (warn-not-fail) but imperfect.
- **Single example.** One passing record. A real ingestion would want a few across
  simple/cascade/novel to exercise the classification branch.

## Blocked / negative results (honest)
- **Sending: blocked by design** (no mailbox/authority). Documented, not faked.
- **Obtaining incidents: not achieved** — depends on an external reply we can't
  produce. The deliverable is the means, not the end.

## Net assessment
Deliverable is **real and tested** (7/7 checks), honest about the gap it does and
does not close, and free of fabricated contacts/numbers. The task's *outcome*
(actual incident data) remains open and correctly out of scope.
