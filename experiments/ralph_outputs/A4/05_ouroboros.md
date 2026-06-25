# A4 — Ouroboros (self-critique, 3 engineers)

## Engineer A — "the schema is prose-shaped, not machine-shaped"
Problems found:
- The spec lists `trap_actions`/`canonical_fix` as `{tool, args}` but never says
  the `tool` vocabulary is *constrained*. A partner will invent tool names we
  don't simulate (`"restart_everything"`), and ingestion silently accepts junk.
- `severity(0..1)` has no validation that it's actually in range in the validator
  pseudocode — easy to forget.
- No `schema_version` enforcement → future drift.
Fix: validator must range-check `severity`, enforce `sustain_ticks>=1`, and the
schema doc must (a) carry a *recommended* tool enum drawn from the repo and
(b) mark `tool` as `string` but warn unknown tools in the validator (warn, not
fail — partners legitimately have tools we'll add). Keep `schema_version` required.

## Engineer B — "the outreach over-promises and the brief over-claims"
Problems found:
- If the email implies we'll co-publish, that's a commitment the sender may not be
  able to make. Must be conditional ("we'd love to explore…").
- The brief risks repeating the very error REV flagged: presenting Snorkel data as
  "real incidents." Need a blunt sentence that this is *third-party-authored*
  evidence, not raw production incidents.
- Contact paths: I must not state a specific human's email. The research only
  confirmed *forms/portals* (partners page, contact page, experts portal) and a
  named public author (Armin Parchami, Sr. Director R&D) — name is citable as a
  *target persona*, but I must NOT fabricate his address.
Fix: soften email to exploratory; add explicit evidence-class disclaimer to brief;
list only form/portal URLs as actionable, name Parchami as "ideal recipient,
route via form / warm intro — do not guess email."

## Engineer C — "tests are too shallow; mapping claim is unverified"
Problems found:
- Spec claims the schema "maps onto scenario YAML" but nothing actually checks the
  example's keys against a real YAML file. That's an untested assertion.
- Only one positive validator test → no confidence the negative paths fire.
- The validator, if hand-rolled, could itself be buggy and pass everything.
Fix: add (1) negative tests for missing-required and conditional-required,
(2) a concrete field-mapping check that loads a real
`scenarios/cidg/generated/*.yaml` and asserts the shared keys
(`root_cause`,`trap_actions`,`canonical_fix`,`slo`,`assertions`) exist in both,
and (3) run all of it for real in 07 with captured output.

## Final filtered spec (deltas applied)
- Validator: range-check `severity∈[0,1]`, `sustain_ticks>=1`, enum checks,
  conditional `why_misleading` for cascade, **warn (not fail)** on tools outside a
  recommended repo-derived enum. Required `schema_version`.
- Brief: add blunt evidence-class disclaimer; contacts = forms/portals only +
  Parchami as target persona with explicit "do not fabricate email."
- Email: exploratory phrasing; placeholders for sender identity.
- Tests: 1 positive + 2 negative validator tests + 1 real-YAML field-mapping
  check, all executed in 07 with real output.
