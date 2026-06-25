# B13 — 01 Plan

## Objective
Design an inter-annotator agreement (IAA) protocol for the REx deterministic diagnosis
judge (`rex/scoring.py:deterministic_judge`), deliver a reusable IAA statistics library
(Cohen's kappa, Fleiss' kappa, Krippendorff's alpha, percent agreement), build a human
relabeling worksheet (CSV of real episodes), and compute a machine-vs-machine agreement
baseline as a sanity check.

## Why this matters
The 30% "diagnosis_correct" reward term is produced by a deterministic keyword judge.
A reviewer will ask: "is that judge VALID — does it agree with human SREs?" IAA is the
standard answer. But the judge is a pure function, so machine-vs-machine kappa is
trivially 1.0. The real validity question (human-vs-machine) needs human labels we do
not have. So the deliverable is: the full protocol + runnable scoring machinery + the
worksheet primed and ready, with human relabeling documented as the blocker.

## Approach
1. `iaa.py` — zero-dependency implementations of percent agreement, Cohen's kappa,
   Fleiss' kappa, Krippendorff's alpha (nominal, missing-data tolerant), mean pairwise
   kappa. Pure functions, validated by unit tests.
2. `build_worksheet.py` — load all real scenarios via `rex.harness.load_scenario`,
   synthesise a deterministic 3-candidate panel per scenario (gold / first red herring /
   generic non-answer), label each with `deterministic_judge`, emit a CSV worksheet with
   a blank `human_label` column for humans to fill in.
3. Machine baseline: re-run the judge (idempotence -> kappa 1.0) AND compare it to a
   second deterministic grader (`mechanism_score >= 0.5`) -> a non-trivial kappa that
   exercises the library on real data.
4. `test_iaa.py` — pytest over the IAA library (known-value, degenerate, missing-data).

## Files to create (all task-namespaced, no shared-core edits)
- `experiments/ralph_outputs/B13/artifacts/iaa.py`
- `experiments/ralph_outputs/B13/artifacts/build_worksheet.py`
- `experiments/ralph_outputs/B13/artifacts/test_iaa.py`
- generated: `relabel_worksheet.csv`, `machine_baseline.json`

## Dependencies
Python 3.13 stdlib only (csv, json, collections, itertools). Reads `rex/scoring.py` and
`rex/harness.py` read-only. No network, no LLM, no cluster.

## Risks
- Machine-vs-machine being trivially 1.0 looks like a non-result -> mitigate by also
  reporting a second-grader kappa and being explicit that human IAA is the real test.
- Krippendorff's alpha is easy to implement wrong -> cover with unit tests incl. missing
  data and a hand-checked Cohen's kappa value.

## Success criteria
- IAA library passes its unit tests.
- Worksheet CSV generated from REAL repo scenarios, parses, has the blank human column.
- machine_baseline.json contains real kappa numbers computed by the library.
- Human relabeling blocker documented honestly; protocol is ready to run on return.
