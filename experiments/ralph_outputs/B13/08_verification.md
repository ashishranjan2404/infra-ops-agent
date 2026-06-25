# B13 — 08 Verification

## Success criteria vs. outcome

| Criterion (from 01) | Status | Evidence |
|---|---|---|
| IAA library passes unit tests | MET | 13 passed (07 §1) |
| Worksheet CSV from REAL repo scenarios | MET | 126 rows from 42 real `load_scenario` scenarios (07 §2-3) |
| Worksheet has blank human column | MET | `human_label` empty; blinded copy drops `machine_label` (07 §3) |
| machine_baseline.json has real kappa numbers | MET | judge-vs-judge 1.0, judge-vs-judge2 0.917 (07 §2) |
| Human relabeling blocker documented honestly | MET | 07 BLOCKER, 09 |
| Protocol ready to run on return | MET | 04 §C step-by-step, library supports >=2 raters + missing data |

## Are the outputs real (not placeholder)?
- `relabel_worksheet.csv` — REAL: every row's `gold_root`/`red_herrings` come from an
  actual scenario YAML via `load_scenario`; `machine_label` is the actual
  `deterministic_judge` output, not hardcoded.
- `machine_baseline.json` — REAL: kappa/agreement computed by `iaa.py` over the 126 real
  labels; judge-vs-judge2 = 0.917 is a genuine non-tautological number.
- `iaa.py` — REAL working code, independently tested.

## Sanity assertions confirmed
- Idempotence: re-running `deterministic_judge` reproduces identical labels -> kappa
  exactly 1.0 (the machine sanity baseline, as predicted for a pure function).
- Non-trivial baseline: a DIFFERENT deterministic grader disagrees on ~4% of episodes
  (kappa 0.917), so the metric is sensitive, not stuck at 1.0.
- Determinism: two runs of `build_worksheet.py` produce byte-identical outputs (no RNG,
  no LLM, no network).

## What is NOT verified
- Human IAA (h-vs-h, h-vs-machine) — BLOCKED on annotators (see 07/09). This is the
  intended-but-unreachable result; the deliverable is the protocol + machinery for it.
- Krippendorff's alpha was validated against hand-computed cases only, not an external
  reference implementation (no such package installed) — carried as residual risk in 09.
