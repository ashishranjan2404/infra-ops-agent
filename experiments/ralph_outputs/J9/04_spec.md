# J9 — Technical spec

## Artifacts & file formats
| File | Format | Contract |
|---|---|---|
| `thesis_claims.json` | JSON | `claims[]` each with `id`, `statement`, `tested_by[]`, `accept_if`, `reject_if`, `review_if`. Plus top-level `conflict_of_interest`. |
| `sre_survey.json` | JSON | `scales{}`, `pages[]` -> `questions[]`. Each question: `id`, `type` in {single,longtext,matrix}, `required` bool, `claim` (claim id or null), optional `scale`, optional `reverse_coded`, optional `screen_out`/`options`/`rows`. |
| `sre_feedback_survey.md` | Markdown | human-readable render of the survey, same order. |
| `sre_interview_guide.md` | Markdown | 45-min semi-structured guide; sections tagged with INT_* ids matching `tested_by`. |
| `recruitment_plan.md` | Markdown | channels table, screener, consent, incentive, target N, timeline. |
| `analysis_template.md` | Markdown | coding scheme, claim-verdict table, scenario review trigger, kappa. |
| `analysis_template.csv` | CSV | 1 header row, 0 data rows. Columns: meta + per-question code columns. |
| `validate_instruments.py` | Python 3.13 stdlib | parses JSON+CSV, enforces the 5 checks below, exit 0/1. |

## Survey question schema (JSON)
```
{ "id": str,              # unique, stable
  "type": "single|longtext|matrix",
  "required": bool,
  "claim": str | null,    # FK -> thesis_claims.claims[].id
  "scale": str?,          # FK -> survey.scales key
  "reverse_coded": bool?,
  "options": [str]?, "rows": [str]?, "screen_out": [str]? }
```

## Claim schema (JSON)
```
{ "id": str, "statement": str,
  "tested_by": [question_id | INT_tag],
  "accept_if": str, "reject_if": str, "review_if": str }   # pre-registered qualitative criteria
```

## Validator checks (test cases)
1. Both JSON files parse. (fail -> exit 1)
2. Every question with non-null `claim` references a real claim id. (dangling ref -> fail)
3. No orphan claim: each claim is covered by >=1 survey question OR an INT_* tag in tested_by.
4. Every question `scale` resolves to a defined scale.
5. CSV header contains meta cols (respondent_id, channel, source) and a recordable column for
   every claim-bearing question (id, id_code, id_realism, id_flags, or scenario_* columns).

Expected on the shipped artifacts: PASS (exit 0), 5 claims, all referenced, ~15 questions.

## Out of scope (the blocker)
Collecting real responses requires human on-call SREs, consent, and scheduling -> cannot be
performed by an autonomous agent. Deliverable is the runnable protocol + validator, not data.
The analysis template and CSV ship EMPTY (0 data rows) by design; populating them is the
human-execution step documented in 07/09.
