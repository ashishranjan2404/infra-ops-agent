# 05_ouroboros — self-critique as 3 different engineers

## Engineer 1 — Data Privacy Engineer (finds real problems)
**P1.1:** The schema's redaction rules R1–R5 describe what *we* do, but the JSON Schema itself
doesn't *encode* them. A partner could submit a record with an absolute timestamp and the schema
would validate it. **Fix:** add format/pattern constraints where feasible (e.g. `t_offset_seconds`
is `integer` not `date-time`; `redacted_text` flagged with a description that it must be
pre-redacted) and make R1–R5 our pre-ingest pipeline, documented as such. Schema can't enforce
"no employee names" — be honest that R3 is a human/regex step, not a schema guarantee.
**P1.2:** `provenance.shared_under: nda` contradicts the v1 ask which is "publicly disclosed
only." **Fix:** v1 records require `disclosed_publicly=true`; `nda/dpa` are reserved for a future
phase and labeled as such so we don't imply we can custody NDA data today.

## Engineer 2 — DevRel / Outreach Specialist (finds real problems)
**P2.1:** Leading every email with "we already model your incident" can read as *we scraped your
postmortem* — slightly threatening. **Fix:** frame it as homage/credit ("your public
postmortem was clear enough that we could faithfully reconstruct it as a benchmark scenario —
credit to your transparency"), and offer to let them review how they're represented. Turns a
threat into a compliment + a reason to engage.
**P2.2:** No clear *low-commitment* CTA. "Share anonymized data" is a big yes/no. **Fix:** make
the primary CTA a 20-minute call OR even just "may we cite that you reviewed our representation
of your public incident?" — a tiny yes that opens the thread (DOL's point from the grill).
**P2.3:** CircleCI brief risk: their 2023 *security* breach makes any "share incident data" ask
land in a paranoid inbox. **Fix:** for CircleCI, explicitly scope to *operational/reliability*
incidents and disclaim we are not asking about the security breach.

## Engineer 3 — Research Integrity / Reproducibility Engineer (finds real problems)
**P3.1:** The package has no record of *what we are already permitted to do*. If a paper reviewer
asks "did you have the right to model these public postmortems?", we have no answer artifact.
**Fix:** add a `provenance` note in each brief: public postmortems are publicly published; we
cite the source and model the *failure mechanism*, not proprietary data. Make this explicit.
**P3.2:** `tracking.csv` with all rows `drafted` and `probability` guesses could be mistaken for
real CRM truth later. **Fix:** add a `notes`/header banner that probabilities are *estimates* and
status is *drafted-not-sent* as of the file date. Also the DO_NOT_SEND banner covers this.
**P3.3:** No success/failure definition that's measurable. **Fix:** state in the spec & summary
that A5's measurable output is "3 review-ready threads + 1 citable permission position," not
"data acquired," so the task can't be falsely marked successful on a hoped-for outcome.

## Final filtered spec (deltas applied)
- Schema: `disclosed_publicly` required true in v1; `shared_under` nda/dpa marked phase-2;
  R3 explicitly documented as a human/regex pre-ingest step, not a schema guarantee. [P1.1, P1.2]
- Emails: reframe warm hook as credit-to-transparency + offer-to-review; add a tiny low-commitment
  CTA; CircleCI scoped to reliability (not the security breach). [P2.1, P2.2, P2.3]
- Briefs: add an explicit "what we are already permitted to do" provenance paragraph. [P3.1]
- Tracking + DO_NOT_SEND: probabilities are estimates, status drafted-not-sent. [P3.2]
- Success defined as threads+permission-position, not data-in-hand. [P3.3]
