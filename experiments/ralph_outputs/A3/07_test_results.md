# A3 — Test results

## validate.py
```
$ python3 experiments/ralph_outputs/A3/artifacts/validate.py
T1 PASS: intake_example.json validates against schema
T2 PASS: missing required field correctly rejected
T3 PASS: tracking_sheet.csv parses (16 rows), enums valid
T4 PASS: category 'saturation' is a valid real-spec category

ALL CHECKS PASSED
EXIT=0
```
`jsonschema` is installed in this env, so T1/T2 ran through the strict **Draft7Validator**
path (not the stdlib fallback). Confirmed:
```
$ python3 -c "import jsonschema" -> ok (Draft7)
```

## JSON validity
```
$ python3 -c "import json; json.load(open('.../intake_schema.json')); print('schema JSON valid')"
schema JSON valid
```
`intake_example.json` also loads as valid JSON (it is parsed by validate.py).

## CSV parse
`tracking_sheet.csv` parses with `csv.DictReader`: 16 data rows, header matches the 11-column
contract, every `status` is `not_started`, every `track` ∈ {community_warm, dua_nonpublic}.

## Mapping sanity check (manual)
Verified by reading `opensre-traj/specs/real/03-incidentio-anetd-cpu.json` that each intake
field has a real-spec target:
- loud_symptom → alert.commonAnnotations.summary ✓
- root_cause → answer.root_cause_subtype ✓
- category → answer.root_cause_category (8-value enum matches) ✓
- trap_action → remediation.trap_actions[] ✓
- correct_fix → remediation.canonical_fix ✓
- causal_chain → answer.causal_chain ✓

## Fixes applied during testing
- None required; validator passed on first run. (Stdlib fallback validator was written
  defensively in case jsonschema were absent; the live env has it.)
