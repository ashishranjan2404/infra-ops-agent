# A10 — Blast-radius metadata for incidents — SUMMARY

## Task
Add blast-radius metadata to each CIDG incident: how many services are affected,
which ones, and a severity tier — derived from each scenario's dependency topology.

## What was delivered
- `artifacts/blast_radius.py` — read-only script that globs all 33
  scenarios/cidg/generated/*.yaml, propagates the root-cause fault via
  reverse-reachability over `required` dependency edges (faults flow to callers),
  assigns a severity tier, and writes a sidecar. Touches no shared/core file.
- `artifacts/blast_radius.json` — {count:33, incidents:[...]}, per incident:
  root node + severity, affected count, affected service list, pct, SEV tier.
- `artifacts/blast_radius.csv` — flat, joinable on incident_id.
- `artifacts/test_blast_radius.py` — 10 unit tests, all passing, incl. a
  real-scenario validation of propagation direction.

## Method
Edge {from:A,to:B} = "A depends on B". A fault at node N impacts every node that
transitively depends on N => reverse BFS from root_cause.location. Tier: SEV1 if
>=4 affected or (sev>=0.9 & cascade), SEV2 if >=2 or cascade, else SEV3.

## Results
- 33 incidents processed; tiers: 24 SEV1 / 1 SEV2 / 8 SEV3; 25/33 multi-service.
- Key finding: mean services_affected == mean topology size == 3.52 — every
  scenario's root cause reaches its whole topology, so blast radius is currently
  near-equal to topology size. The 8 synthetic single-node scenarios are SEV3; the
  historical multi-service cascade scenarios are SEV1/SEV2. Honest limitation in
  09_critique.md: mechanism is correct and tested, but discriminative payoff is
  bounded by the generator always producing full-graph blasts.

## Status: completed (real plan + spec + runnable artifact + passing tests).
