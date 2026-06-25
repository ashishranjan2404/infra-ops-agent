# G5 — 06 Implementation

## What I built (real artifacts)
1. **`artifacts/positioning_matrix.md`** — the primary deliverable. A 5-dimension × 4-column
   markdown table (us / SREGym / Komodor / Datadog Bits AI) across: Open benchmark, Trap-action
   safety, Training method, Deployment posture, Evaluation rigor. Includes a category disclaimer,
   per-dimension prose, an explicit "where our position is honestly weaker" section, and a sources
   block. Every competitor cell carries `[Sn]` citation tags.
2. **`artifacts/sources.json`** — machine-readable source registry, 11 sources (S1–S11), each with
   url / who / claim / verification / as_of. Verification is one of `primary`, `vendor-stated`,
   `self-reported`, `third-party-review`.
3. **`artifacts/validate_matrix.py`** — Python 3 stdlib validator. Checks C1 (5×4 structure),
   C2 (every competitor cell cited), C3 (every tag resolves), C4 (source field integrity),
   C5 (both vendor columns cite a `vendor-stated` source — the honesty guard). Has a `--selftest`
   mode (T1 happy path, T2 missing tag, T3 unresolved tag, T4 source missing url).

## Honest claims grounded in sources
- **Us (S1):** reward formula with explicit −0.60 trap penalty, frozen swappable policy,
  within-group reward spread, GKE *test* cluster, 0.86 ceiling = escalate-the-unsolvable.
  (`/Users/mei/rl/ARCHITECTURE.md`.)
- **SREGym (S2,S3,S4):** open-source live benchmark, 90 problems, diagnosis 38.9–72.6% /
  mitigation 57.3–78.5%; positioned as a training ground but provides environment not algorithm.
- **Komodor (S5,S6,S7):** deployed self-healing product, vendor-stated 95% accuracy and Cisco
  40%/80% numbers, human-or-no-human remediation. Numbers quarantined to the Komodor column and
  flagged vendor-stated.
- **Datadog Bits AI (S8–S11):** deployed agent on live telemetry, 2,000+ environments, internal
  proprietary benchmark, "~2× faster/more accurate" (vendor-stated, no independent RCA benchmark).

## Shared-core-file safety
No shared core file was edited. Only `ARCHITECTURE.md` was *read* (not modified). All new files
live under `experiments/ralph_outputs/G5/`. No `rex/`, `sim/`, `agent/`, `experiments/*.py`,
`ralph_status.json`, or another task's directory was touched.

## Key design decisions (from grill + ouroboros)
- Lead with **category honesty**, not a victory lap — we are a benchmark/data engine, two of the
  four are deployed products.
- Keep the two dimensions where we **tie or lose** (Open benchmark = tie w/ SREGym; Deployment
  posture = we lose) and state it plainly, so the matrix isn't a rigged scorecard.
- Validator scope honestly downgraded to "citation hygiene + vendor-flag discipline" — it proves
  form, not factual truth.
