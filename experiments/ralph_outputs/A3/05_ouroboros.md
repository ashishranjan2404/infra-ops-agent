# A3 — Ouroboros (3 self-critiques, each finds real problems)

## Engineer A — "the schema is too loose to be useful"
Problem found: the spec says intake "maps 1:1" to real-spec, but real-spec scenarios need
*evidence* (k8s_pods, prometheus_metrics, traces) to be runnable. A donated 5-field form
cannot produce evidence. So calling this "a runnable scenario with minimal transform"
overclaims — the transform is actually substantial (a human must author synthetic evidence
consistent with the donor's root_cause/trap).
Fix: downgrade the claim. The intake schema captures the *ground-truth labels*
(loud_symptom/root_cause/trap/fix/causal_chain); evidence authoring is a separate, explicitly
human step. Document this honestly in implementation + critique, and add a `causal_chain`
field so the labels are rich enough to drive evidence authoring later.

## Engineer B — "the validator doesn't actually prove the check bites"
Problem found: a validator that only checks the happy-path example proves nothing — if the
schema were empty, the example would still pass. Need a negative test.
Fix: validator must run T2 — load the example, delete a required field, assert it FAILS.
Without a failing-case assertion the validation is theater.

## Engineer C — "the outreach is legally naive / could harm the project"
Problem found: templates that ask companies for "incident channel transcripts" invite
sharing of customer PII and security details; if a template implies we'll publish it, no
counsel approves it, and it could damage the relationships the project already has
(incident.io, HUD community). Also: an autonomous agent drafting and *sending* such asks
would be reckless.
Fix: (1) every template leads with "de-identified, you redact before sending, we never
publish without written OK"; (2) add `consent_anonymization.md` as a hard gate referenced by
every template; (3) state plainly that sending is a human action — the agent only drafts.
Also add a `consent` object to the schema so no incident enters the pipeline without an
explicit `granted:true`.

## Final filtered spec (deltas applied)
- Reframe intake as **label capture**, not full-scenario capture; evidence authoring is a
  separate human step (Eng A).
- Validator MUST include a negative test that a missing required field fails (Eng B).
- Templates are anonymization-first, redact-before-send, never-publish-without-OK; sending is
  a human action; schema carries a required `consent` object (Eng C).
- Keep `causal_chain` field so labels are rich enough to drive later evidence authoring.
