# A3 — Implementation

This is an outreach/process task. "Built" = real, valid, runnable outreach machinery.
All artifacts under `experiments/ralph_outputs/A3/artifacts/`. No shared core files edited.

## Artifacts produced
1. **target_companies.md** — 16 targets across two tracks (`community_warm`, `dua_nonpublic`),
   each with reachability (warm/cold), expected provenance, and rationale. Honest exclusion of
   cold-FAANG (~0% yield). Funnel math to reach 10+ incidents.
2. **outreach_templates.md** — 4 channel templates (cold_email, warm_intro, community_dm,
   public_cfc), each anonymization-first / reciprocity-first, with merge fields, all
   referencing the consent gate; explicit "sending is a human action."
3. **intake_schema.json** — draft-07 JSON Schema. Light, donor-fillable; required fields
   include `root_cause` and `trap_action` (the first-party ground truth) plus a required
   `consent` object and a `provenance` enum. Documented 1:1 mapping to `specs/real/*.json`.
4. **intake_example.json** — a worked, de-identified, non-public donated incident
   (`acme_redis_failover_thundering_herd`) that validates against the schema and exhibits the
   cascade shape (loud victim symptom = checkout latency; trap = rollback + mass restart;
   root cause = synchronized reconnect storm after Redis failover).
5. **consent_anonymization.md** — consent tiers, a 1-page DUA term sheet, a donor-run
   de-identification checklist, and the provenance-defensibility note.
6. **tracking_sheet.csv** — 16-row campaign tracker; `status`/`track` constrained to enums.
7. **validate.py** — runs T1-T4; uses real `jsonschema` (Draft7) when available, with a
   stdlib fallback validator.

## Key implementation decisions (traceable to grill/ouroboros)
- `provenance` enum + required `consent` object → lets us filter the genuinely non-public
  subset that carries the novelty claim (AAAI/RLE).
- Short form, but `root_cause` + `trap_action` required free-text (SMR/PSRE compromise).
- Reframed intake as **label capture**, not full-scenario capture: evidence
  (k8s_pods/metrics/traces) is authored by a human later from the donor's labels +
  causal_chain. This corrects the "maps 1:1 with minimal transform" overclaim (Ouroboros A).
- validate.py includes a **negative test (T2)** so the validation isn't theater (Ouroboros B).
- Templates are redact-before-send / never-publish-without-OK; sending is human (Ouroboros C).

## Not done (honest)
- No emails actually sent, no DUA signed, no incidents in hand — those are human/legal actions
  outside an autonomous agent's reach (see 07 + 09).
