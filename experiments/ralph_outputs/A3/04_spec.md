# A3 — Technical Spec

## 1. Intake schema (`intake_schema.json`)
JSON Schema (draft-07). A donated incident MUST map onto the existing
`opensre-traj/specs/real/*.json` shape so it becomes a runnable scenario. The intake schema
is a **lighter superset** that a non-expert donor can fill; a transform step (documented, not
auto-run here) expands it into the full real-spec.

Required top-level fields:
- `incident` (string, snake_case id)
- `source_company` (string; may be "anonymized")
- `provenance` (enum: `public_postmortem` | `first_party_donated` | `first_party_nonpublic`)
- `consent` (object: `{granted: bool, anonymized: bool, contact: string|null, dua: bool}`)
- `loud_symptom` (string — the misleading alert/symptom)
- `root_cause` (string — REQUIRED free-text, first-party ground truth)
- `trap_action` (string — REQUIRED free-text; the naive fix that worsened it)
- `correct_fix` (string)
- `category` (enum matching real-spec `root_cause_category`: saturation, network_fault,
  config_error, dependency_failure, bad_deploy, resource_exhaustion, node_failure,
  data_quality)

Optional but recommended:
- `provider` (string, e.g. k8s/aws/gcp)
- `timeline` (array of `{ts, actor, action, effect}`)
- `causal_chain` (string)
- `source_url` (string|null — null/absent for non-public)
- `severity` (enum: info|warning|critical)
- `difficulty` (int 1-5)

Mapping to real-spec fields (transform target):
| intake field      | real-spec field                         |
|-------------------|------------------------------------------|
| incident          | incident / source_company                |
| loud_symptom      | alert.commonAnnotations.summary          |
| root_cause        | answer.root_cause_subtype                |
| category          | answer.root_cause_category               |
| trap_action       | remediation.trap_actions[]               |
| correct_fix       | remediation.canonical_fix                |
| causal_chain      | answer.causal_chain                      |
| provenance        | (new) — used for novelty filtering        |

## 2. Target list (`target_companies.md`)
Two tracks, each row = `name | track | reachability(warm/cold) | expected_provenance |
rationale`. >=15 rows total. Tracks: `community_warm`, `dua_nonpublic`.

## 3. Outreach templates (`outreach_templates.md`)
Four templates, each with subject + body + merge fields `{{name}} {{company}} {{warm_ref}}`:
1. cold_email — narrow, anonymized, reciprocity-first.
2. warm_intro — leverages an existing contact.
3. community_dm — Slack/Discord/Reddit short form.
4. public_cfc — a public "call for incident contributions" blurb.

## 4. Tracking sheet (`tracking_sheet.csv`)
Columns: `target,track,channel,owner,status,first_contact,last_touch,next_action,
provenance_expected,incident_id,notes`.
`status` enum: `not_started,contacted,replied,negotiating,received,declined,no_response`.

## 5. Validator (`validate.py`)
- Loads `intake_schema.json`; validates `intake_example.json`.
- Uses `jsonschema` if importable; else a minimal stdlib check of required fields + enums.
- Parses `tracking_sheet.csv` with `csv.DictReader`; checks header + that every `status` and
  `track` value is in the allowed enum.
- Exit 0 on success, non-zero with message on failure.

## 6. Test cases
- T1: example validates against schema (required fields present, enums valid).
- T2: a deliberately-broken copy (missing `root_cause`) FAILS — proves the check bites.
- T3: CSV parses, header matches, all status/track enums valid.
- T4: every `category` in example is in the real-spec category set.
