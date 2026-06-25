# 04_spec — technical spec for the outreach package

## A. File layout
```
experiments/ralph_outputs/A5/
  artifacts/
    briefs/{circleci,incidentio,cloudflare}.md
    outreach/{circleci,incidentio,cloudflare}_email.md
    anonymization_spec.md
    anonymization_schema.json
    tracking.csv
    validate.py
    DO_NOT_SEND.md
```

## B. Brief format (each brief is a markdown doc with these sections)
1. `# <Company>` + one-line identity.
2. `## Warm hook` — the exact `cidg` scenario file(s) we already model.
3. `## Why they'd say yes` — strategic incentive specific to them.
4. `## The ask` — least-sensitive useful slice.
5. `## Contact path` — role-based / public channels ONLY, each tagged `[VERIFY]`.
6. `## Objection handling` — 3 likely objections + our answer.
7. `## Yield estimate & fallback` — High/Med/Low + what we do on a no.

## C. Email format
- Subject line, body ≤ 220 words, single concrete ask, attachment reference, signature
  placeholder `<Researcher Name / SRE-Degrees project>`. Plus a ≤ 60-word DM/LinkedIn variant.

## D. Anonymization schema (JSON) — contract for shared records
`anonymization_schema.json` is a JSON Schema (draft 2020-12) describing ONE anonymized incident
record we accept:
```
incident_id        string  (partner-assigned opaque id, no internal ticket numbers)
disclosed_publicly boolean (must be true for v1 ask)
failure_class      enum    (net_delay|config_bloat|resource_exhaustion|dependency|deploy|other)
timeline[]         {t_offset_seconds:int, event_type:enum, redacted_text:string}
alert_shapes[]     {signal:string, threshold_relation:enum(gt|lt|eq), unit:string}
remediation_steps[] string
provenance         {public_url:string|null, shared_under:enum(public|nda|dpa)}
```
Redaction rules (enforced by us before storage):
- R1 No absolute timestamps — only offsets from t0.
- R2 No hostnames/IPs/customer names — replace with role tokens (`web-app`, `edge-dns`...).
- R3 No employee names/handles in `redacted_text`.
- R4 No raw alert *values*, only threshold *relations* + units (k-anonymity on magnitudes).
- R5 Drop any field the partner marks `sensitive:true`.

## E. tracking.csv columns
`company,contact_role,channel,status,probability,last_touch,next_action,notes`
- status ∈ {not_started, drafted, sent, replied, agreed, declined}
- For A5 every row is `drafted` (sending out of scope).

## F. validate.py contract
- `load_csv(path) -> list[dict]`; assert header == expected 8 columns; assert each row's
  `status` and `probability` in allowed sets.
- `load_schema(path) -> dict`; `json.load` must succeed; assert top-level `$schema`,
  `properties` keys cover the 7 fields in section D.
- `main()` prints `OK: N companies, schema fields=M` and exits 0; exits 1 + message on any
  violation. Stdlib only (`csv`, `json`, `sys`, `pathlib`).

## G. Test cases (run in step 07)
- T1 `validate.py` exits 0 on the real artifacts.
- T2 each email body word count ≤ 220 (shell `wc -w` sanity).
- T3 every `cidg` file cited in a brief actually exists on disk.
- T4 no `[VERIFY]`-free personal email address slips in (grep for `@gmail|@yahoo` etc. = none).
