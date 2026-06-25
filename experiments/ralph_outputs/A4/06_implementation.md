# A4 — Implementation

## What I built (all under `experiments/ralph_outputs/A4/artifacts/`)
1. **`snorkel_contact_brief.md`** — researched contact & positioning brief. Snorkel
   profiled from live research (RL-environments blog, partners page): RL gyms with
   verifiable rewards, Expert Data-as-a-Service, **$3M Open Benchmarks Grants**,
   research-collaboration track. Real contact channels only (partner form, contact
   page, LinkedIn); **Armin Parchami (Sr. Director R&D)** named as target persona
   with an explicit "do not fabricate his email." Includes the blunt evidence-class
   honesty section and the out-of-scope note.
2. **`outreach_email_snorkel.md`** — full email (subject + ~210-word body) framed as
   co-building an open SRE incident-response RL benchmark, with a tiered ask
   (open benchmark + NDA'd structured-records fallback) and a 30-min CTA; plus an
   ≤90-word short variant for a warm intro / DM. Sender identity left as
   `<PLACEHOLDER>` tokens (no fabricated person).
3. **`data_sharing_checklist.md`** — 7-phase gating checklist (authority → NDA →
   anonymization/PII → license → security/transfer → retention → publication),
   each item a human-resolvable yes/no. Encodes "no raw prod logs" and "reject
   pii_status=present."
4. **`incident_ingest_schema.json`** (draft-07) + **`incident_ingest_schema.md`**
   (human contract) — `IncidentRecord` capturing the **verifier contract**
   (`trap_actions`, `canonical_fix.steps`, `slo`, `assertions`) as a superset of the
   real `scenarios/cidg/generated/*.yaml` keys + catalog narrative fields +
   `INCIDENT_DATASET.md` classification taxonomy + in-band legal/PII metadata in
   `source`.
5. **`example_record.json`** — a complete, passing cascade example (CDN cache
   stampede) using repo-consistent tool names.
6. **`validate_schema.py`** — stdlib-only validator (required/type/enum/pattern/
   range/minItems + the cascade→why_misleading conditional + unknown-tool WARN).

## Design decisions traceable to the grill / ouroboros
- Collaboration framing + tiered ask (SMR/PSRE/RLE) → email + brief.
- Honest evidence-class disclaimer (REV) → brief §5, checklist Phase 6.
- Verifier-contract-shaped schema (RLE) → schema mirrors `trap_actions`/
  `canonical_fix`/`slo`/`assertions`.
- Validator hardening (Ouroboros A): severity range, sustain_ticks≥1, conditional,
  unknown-tool warn-not-fail, required schema_version.
- Real-YAML mapping check (Ouroboros C) → executed in 07, 51 scenario files,
  shared keys present in both.

## Proposed change to shared core (NOT applied — parallel-safety rule)
The natural follow-up is a `partner_record → scenario YAML` converter living in the
pipeline (e.g. a new `scenarios/cidg/ingest_partner.py`). I did **not** create or
edit any shared core file. The mechanical mapping is documented in
`incident_ingest_schema.md` ("a normalized partner record is convertible to a
runnable scenario YAML with a mechanical mapping…"). If/when partner data arrives,
that converter is a small, well-specified task — the schema is the hard part and
it's done and validated here.

## Honest scope note
No email was sent; no partnership initiated. This worker cannot send mail or commit
a data agreement. The deliverable is the send-ready package a human uses.
