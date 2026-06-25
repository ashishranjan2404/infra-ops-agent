# A17 — Verification against success criteria

| Success criterion (from 01_plan) | Met? | Evidence |
|----------------------------------|------|----------|
| Covers all 7 Datasheet sections + reproducibility appendix | **Yes** | DATA_CARD §1–7 (Motivation→Maintenance) + §8 Appendix; 8 `##` headers (T6) |
| Every quantitative claim reproducible | **Yes** | `compute_stats.py` derives all numbers; T5 spot-checks 5 figures == stats.json |
| Honest limitations | **Yes** | §8E lists 8 limitations: synthetic/not telemetry, single-platform, small topo, contamination, keyword-judge fragility, empty URLs, registry gap, unused fields |
| All corpus YAML/JSON parse cleanly | **Yes** | T2 (51/51 YAML), T3 (registry + stats JSON) |
| No shared-core file edited | **Yes** | Only `experiments/ralph_outputs/A17/*` written; core read-only (see 06) |
| Grounded in actual `scenarios/cidg/generated/` | **Yes** | Composition, provenance, fix-tools, thesis stats all derived from the live corpus |

## Are the outputs real (not placeholder)?
- `compute_stats.py` is a runnable, tested script (exit 0, asserts invariants).
- `stats.json` is its actual output, not hand-authored.
- `DATA_CARD.md` numbers are copied from `stats.json` and re-verified by T5.
- The scoring contract is transcribed from `rex/scoring.py` (reward weights L22;
  `deterministic_judge` L79–86; `JUDGE_MODE` L26/L112–118), not invented.

## Reproducibility note
For a fixed corpus commit, `python3 compute_stats.py` deterministically reproduces the
composition tables. The card explicitly decouples its (dated) snapshot from the live,
growing corpus — so the deliverable stays correct as the corpus expands.

**Verdict:** all success criteria met. Deliverable is real and reproducible.
