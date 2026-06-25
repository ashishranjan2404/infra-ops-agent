# A17 — Data Card / Datasheet for the SRE-Degrees Benchmark — Plan

## Objective
Produce a complete, AAAI-reproducibility-grade **DATA_CARD.md** for the SRE-Degrees
benchmark, following the *Datasheets for Datasets* (Gebru et al., 2021) / Hugging Face
data-card format. The card must be **grounded in the actual contents** of
`scenarios/cidg/generated/` — not aspirational marketing — covering composition,
collection process, provenance (postmortems), preprocessing, recommended uses,
limitations, and licensing/maintenance.

## Why this matters
AAAI (and most ML venues) now expect a datasheet for any released benchmark.
Reviewers use it to judge construct validity, contamination risk, and reproducibility.
A vague or fabricated card is a rejection vector. The card must reflect what is *really*
on disk: 35 scenario YAMLs, a 32-entry registry, 14 failure classes, all GKE/LKE,
all `chaos_kind: exec`, 27/35 cascading with a buried smoking gun.

## Approach
1. Enumerate the real corpus: count YAMLs, parse every file, tally failure_class,
   clouds, chaos_kind, canonical fix tools, assertion flags, families.
2. Reconcile registry.json (32 entries) vs YAML files on disk (35) — document the gap.
3. Map provenance: each `meta.source` ties a scenario to a real-world postmortem
   (Facebook BGP 2021, Cloudflare WAF, GitHub MySQL, Knight Capital, etc.) or to a
   synthetic "leaf" template (40–47, 20–22, 30).
4. Write DATA_CARD.md using the 7 Datasheet sections + a reproducibility appendix
   (schema spec, seed/determinism, judge scoring contract).
5. Validate: YAML-parse every scenario, JSON-parse the registry, markdown sanity.

## Files to create (all task-namespaced — NO shared-core edits)
- `experiments/ralph_outputs/A17/artifacts/DATA_CARD.md` — the deliverable.
- `experiments/ralph_outputs/A17/artifacts/compute_stats.py` — reproducible stats script
  (re-derives every number in the card from disk).
- `experiments/ralph_outputs/A17/artifacts/stats.json` — the computed composition table.
- Step files 01–10 + SUMMARY.md + result.json.

## Dependencies
- `pyyaml` (already in repo deps), `python3`, stdlib `json`/`glob`/`collections`.
- Read-only access to `scenarios/cidg/generated/`, `rex/scoring.py` (for the judge contract).

## Risks
- **Number drift**: if I hand-type counts they will be wrong. Mitigation: derive ALL
  numbers from `compute_stats.py` and paste its output; never invent.
- **Provenance overclaiming**: `meta.urls` is empty for every scenario, so I cannot cite
  exact postmortem URLs. Mitigation: state titles/dates as given in `meta.source`, and
  flag the missing-URL limitation explicitly rather than fabricating links.
- **Registry/YAML mismatch** could look like a bug. Mitigation: document it as a known
  composition note (3 scenarios not yet indexed).

## Success criteria
- DATA_CARD.md covers all 7 Datasheet sections + reproducibility appendix.
- Every quantitative claim is reproducible by running `compute_stats.py`.
- Limitations section is honest (synthetic sim, no real telemetry, GKE/LKE-only,
  empty URLs, registry gap).
- All YAML/JSON in the corpus parse cleanly (validated in 07).
- No shared-core file edited.
