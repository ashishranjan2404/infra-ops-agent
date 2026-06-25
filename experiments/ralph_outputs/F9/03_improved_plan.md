# 03 — Improved Plan

## What changed vs. 01 (driven by the grill)
- **Added an aggregate Summary section** (cascade count, hidden-root-cause count,
  failure-class histogram). Accepted from AAAI+PSRE: surfaces realism honestly in
  aggregate instead of forcing fake citations per row.
- **Added per-incident difficulty signals** (topology node count, cascade flag).
  Accepted from RLE: catalog should reflect difficulty, not just identity.
- **Hardened extraction** with `.get()` + per-file try/except that warns and skips
  rather than aborting. Accepted from DEVO.
- **Dual output (MD primary, JSON secondary)** with deterministic ordering (sorted by
  filename) for a CI diff gate. Accepted from DEVO/SMR, but framed MD as the primary
  paper deliverable per SMR's caution.
- **Key on filename, not id** for ordering/dedup, because several files share an id
  prefix (`80-*`, `81-*`, `82-*`).

## Critiques accepted
- Show `source` verbatim, including "Synthetic simple incident (...)" — do not invent
  URLs (PSRE).
- Order matters in fixes → render `canonical_fix.steps` in order with numbers (PSRE).

## Critiques rejected (and why)
- AAAI's implied "require a real URL per incident": rejected — the substrate is
  deliberately part-synthetic; fabricating citations would be dishonest. Instead the
  source field is shown as-is and the summary makes the synthetic/real mix visible.
- RLE's "list every raw key the harness uses": partially rejected — listing internal
  sim keys (e.g. `fault.sim.set`) bloats the catalog without helping a reader. Kept
  the human-meaningful subset (root cause, fix, cascade, topology size).

## Final deliverable shape
`gen_incident_catalog.py` → `incident_catalog.md` + `incident_catalog.json`, plus
`test_catalog.py`. One command, deterministic, defensive.
