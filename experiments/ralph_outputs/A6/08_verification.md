# A6 — 08 Verification

## Success criteria (from 01) vs. evidence
| Criterion | Status | Evidence |
|----------|--------|----------|
| 10 new, uniquely-named YAMLs | MET | files 80–89 in `scenarios/cidg/generated/`, descriptive slugs |
| Each parses as YAML | MET | T1: 10/10 PARSE OK |
| Each passes `sim.spec validate` (0 errors) | MET | T2: 10/10 specs valid |
| No duplicate ids vs existing corpus | MET | T3: DUPLICATE IDS: none |
| Distinct real postmortems, coherent root/trap/fix | MET | 8 distinct root-cause kinds; each maps to a documented incident |
| No edits to shared `.py` / existing YAML / registry | MET | only new files created; `registry.json`, `sim/*.py`, `tools_registry.json` untouched |

## Are the outputs real (not placeholder)?
Yes. Each YAML is a fully-populated, schema-valid spec that loads via `sim.spec.load_spec` and
passes the same validator that gates the existing 33-scenario corpus. The incidents are real and
well-known (GitLab 2017 DB deletion, Cloudbleed, Travis CI secret leak, Roblox 73h Consul outage,
Fastly 2021-06-08, Reddit Pi-Day 2023, Honeycomb retry storm, AWS S3 2017-02-28, Stripe Redis,
Monzo Cassandra). Each gold fix is the operationally-correct in-vocab action, with abstractions
spelled out in `ordering_notes`.

## Independent re-check
- Validator run scoped to exactly the 10 authored paths → 10/10 OK.
- Dup-id scan over the entire `generated/*.yaml` glob → none.
- Spot structural check: every file has ≥1 required/discovery edge (cascade) and one buried
  `get_logs` smoking gun on the root (buried_gun_exists) → assertions are satisfiable.

Verdict: **all success criteria met.** The deliverable is the 10 validated scenario YAMLs; no
downstream training/eval run was in scope for A6 (see 09 for the honest scope boundary).
