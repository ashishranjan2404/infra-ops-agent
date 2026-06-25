# A9 — 01 Plan

## Objective
Label each CIDG incident scenario with the **real-world MTTR** (mean/total time to
resolution) drawn from its **source postmortem**, so a downstream analysis can
correlate human MTTR against agent/sim difficulty. Where MTTR is unknown, mark it
**unknown** — never invent a number.

## Inputs (real repo assets)
- `scenarios/cidg/generated/*.yaml` (32 scenarios) — each `meta.title`/`meta.source`
  names either a synthetic generator family ("Synthetic simple incident (...)",
  "SREGym", "novel") or a dated public incident (GitHub, Cloudflare, Slack,
  Facebook, AWS, Azure, Knight Capital, Mozilla, etc.).
- `scenarios/cidg/generated/registry.json` — structural metadata per incident.

## Approach
1. Enumerate all YAMLs; extract `incident_id`, `yaml_file`, `title`.
2. Classify each as **real** (dated public postmortem) vs **synthetic/benchmark/novel**.
3. For real incidents, attach MTTR from the public postmortem with: value (minutes),
   basis (documented/approximate/unknown), source citation (org + report + URL),
   and a confidence level. For synthetic ones, `confidence=not_applicable`.
4. Emit a **sidecar** `mttr_labels.csv` (source of truth) + a `build_mttr_json.py`
   that validates and renders `mttr_labels.json`.
5. Add a runnable **correlation-analysis stub** `correlate_mttr.py` that joins MTTR
   labels with a pluggable difficulty signal (external scores, or a structural proxy
   from the YAML) and reports Pearson + Spearman, dropping unknown-MTTR rows.

## Files to create (all under A9/, no shared-core edits)
- `artifacts/mttr_labels.csv`
- `artifacts/build_mttr_json.py` (+ generated `artifacts/mttr_labels.json`)
- `artifacts/correlate_mttr.py`

## Dependencies
Python 3 stdlib only (csv, json, math). No numpy/scipy/PyYAML — runs in base env.

## Risks
- **Fabrication risk**: tempting to assign plausible-looking MTTRs. Mitigation: only
  label when I can cite a specific postmortem; everything else is `unknown`.
- **Date/signature mismatch**: some titles use dates that don't match the canonical
  public event (e.g. AWS Kinesis 2024-07-30 vs the famous 2020-11-25). Mark unknown
  and note the suspected conflation rather than guessing.
- **Granularity**: MTTR is outage-level, not per-service; the sim has per-node SLOs.
  Documented as an `mttr_basis` caveat.

## Success criteria
- Every one of the 32 incidents has a row (no silent drops).
- Real incidents have either a cited MTTR or an explicit `unknown` with a reason.
- CSV->JSON build passes a schema/range/invariant validator.
- Correlation stub runs end-to-end on repo assets and drops unknowns transparently.
