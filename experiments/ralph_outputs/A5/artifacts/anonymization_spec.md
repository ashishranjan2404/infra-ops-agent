# Anonymization spec — shared incident data (SRE-Degrees, v1)

This is the data-handling contract we offer partners (CircleCI, incident.io, Cloudflare). It is
intentionally conservative: **v1 covers only incidents the partner has already publicly
disclosed.** NDA/DPA-gated data is a phase-2 conversation, not part of this offer.

## 1. What we ask for (per incident)
A single anonymized record matching `anonymization_schema.json`:
- `incident_id` — a partner-assigned opaque id (NOT an internal ticket number).
- `disclosed_publicly` — must be `true` for v1.
- `failure_class` — one of our enum buckets.
- `timeline[]` — `{t_offset_seconds, event_type, redacted_text}`.
- `alert_shapes[]` — `{signal, threshold_relation, unit}` — *shapes only, never values*.
- `remediation_steps[]` — ordered, redacted.
- `provenance` — `{public_url, shared_under}` (`shared_under` = `public` in v1).

## 2. Redaction rules (applied by US before storage)
- **R1 — No absolute time.** Only `t_offset_seconds` from t0. We drop any wall-clock timestamp.
- **R2 — No infra identifiers.** Hostnames, IPs, regions, customer names → role tokens
  (`web-app`, `edge-dns`, `ingress-gw`, ...), matching our `cidg` topology vocabulary.
- **R3 — No people.** Employee names / handles removed from `redacted_text`. *This is a
  human + regex pre-ingest step, not enforced by the JSON Schema — we state that honestly.*
- **R4 — No alert magnitudes.** We keep `signal` + `threshold_relation` (gt|lt|eq) + `unit`,
  never the numeric value/threshold (k-anonymity on magnitudes).
- **R5 — Honor `sensitive:true`.** Any field the partner flags is dropped before storage.

## 3. What the schema can and cannot enforce
- **Can:** structural shape, enums, `t_offset_seconds` is an integer (so no `date-time` slips
  in), `disclosed_publicly` required.
- **Cannot:** guarantee free-text fields contain no names/IPs — R2/R3 are our pipeline's job.
  We do not over-claim a cryptographic guarantee.

## 4. Custody, retention, legal
- Storage: only the redacted record above; raw submissions deleted after redaction.
- Retention: for the life of the benchmark; partner may request removal at any time.
- Legal: v1 = public incidents only. We will sign the partner's DPA/NDA for any phase-2 data.
- Attribution: we cite the public source and, with permission, "reviewed by <partner>."

## 5. Stretch (clearly optional, not part of v1 custody offer)
Aggregated/anonymized post-incident exports (esp. incident.io, whose product is this) under a
signed DPA — separate conversation.
