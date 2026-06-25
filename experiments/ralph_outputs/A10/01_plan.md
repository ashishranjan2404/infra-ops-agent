# A10 — Blast-radius metadata for incidents — 01 Plan

## Objective
For every incident scenario in `scenarios/cidg/generated/*.yaml`, derive a
**blast-radius** record: how many services the root-cause fault affects, *which*
services, and a severity tier — by propagating the fault through the scenario's
declared dependency topology. Emit a JSON + CSV sidecar keyed by incident id.

## Approach
1. Parse each YAML's `topology.nodes` and `topology.edges`.
2. Read edge semantics: `{from: A, to: B, type: required}` = "A depends on B".
   A fault at the root cause node `N` impacts every node that (transitively)
   *depends on* `N` → walk edges in reverse (`to → from`) via BFS from `N`.
3. Affected set = reverse-reachable closure of `root_cause.location` (incl. root).
4. Severity tier from (#affected, `root_cause.severity`, `assertions.cascades`):
   SEV1 (>=4 affected, or sev>=0.9 + cascade), SEV2 (>=2 or cascade), SEV3 (1).
5. Write `blast_radius.json` (full detail) + `blast_radius.csv` (flat) sidecar.

## Files to create (all under my task dir — NO shared files touched)
- `artifacts/blast_radius.py` — the computer (read-only over YAMLs).
- `artifacts/blast_radius.json`, `artifacts/blast_radius.csv` — outputs.
- `artifacts/test_blast_radius.py` — unit tests for the propagation logic.

## Dependencies
- `pyyaml` (already in repo requirements). Stdlib only otherwise.

## Risks
- **Edge direction ambiguity**: if I invert it, blast radius is wrong. Mitigate
  by validating against a hand-checked scenario (slack-consul-cache-db).
- Root cause node missing from topology (malformed YAML) → fall back to {root}.
- Tier thresholds are a judgement call → document and keep them tunable.

## Success criteria
- Script runs over all ~33 scenarios with no error.
- Each incident gets services_affected count + list + tier.
- Propagation direction validated on >=1 known scenario.
- Tests pass. No existing YAML or `rex/`,`sim/`,`agent/` file modified.
