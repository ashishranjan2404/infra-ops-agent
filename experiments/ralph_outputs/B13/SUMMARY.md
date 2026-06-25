# B13 — SUMMARY

**Task.** Compute inter-annotator agreement (IAA) on the deterministic diagnosis judge.
Because `rex/scoring.py:deterministic_judge` is a pure function, design the IAA protocol,
write a Cohen's-kappa / Krippendorff's-alpha script, build a human relabeling worksheet,
and compute machine-vs-machine agreement as the sanity baseline.

## Delivered (all in `artifacts/`, no shared-core edits)
- **iaa.py** — zero-dependency IAA library: percent agreement, Cohen's kappa, Fleiss'
  kappa, Krippendorff's alpha (nominal, missing-data tolerant), mean pairwise kappa.
- **test_iaa.py** — 13 pytest cases, all passing.
- **build_worksheet.py** — loads 42 real scenarios, labels a deterministic 3-candidate
  panel each with the real judge, emits the worksheet + machine baseline.
- **relabel_worksheet.csv** (126 episodes) + **relabel_worksheet_blinded.csv** (the
  machine_label-hidden copy that ships to human annotators).
- **machine_baseline.json** — real computed agreement.

## Results
- IAA library: 13/13 tests pass.
- Machine sanity baseline: judge-vs-itself Cohen kappa = 1.0 (idempotence, as expected
  for a deterministic function); judge vs a second deterministic grader
  (mechanism_score>=0.5) kappa = 0.917, percent agreement 0.9603 — the honest
  non-trivial baseline.
- Worksheet: 126 real episodes across 42 scenarios, primed and blinded for humans.

## Blocker (honest)
Human relabeling is unavailable (no annotators/budget this week), so human-vs-human and
human-vs-machine kappa — the actual validity result — are not produced. The full protocol
is in 04_spec.md section C, and the machinery supports it unchanged once labels arrive.
Per the brief this is a documented downstream blocker; the deliverable (tested library +
primed worksheet + machine baseline + protocol) is complete.

## Status: completed (downstream human study blocked, documented)
