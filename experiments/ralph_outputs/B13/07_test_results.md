# B13 — 07 Test Results

## 1. IAA library unit tests
```
$ python3 -m pytest test_iaa.py -q
.............                                                            [100%]
13 passed in 0.01s
```
PASS — all 13 cases (perfect, chance, hand-checked Cohen value, worse-than-chance,
degenerate constant raters, length/empty errors, Fleiss perfect + uneven-rater error,
Krippendorff perfect / missing-data / partial-disagreement, mean-pairwise + <2-rater
error).

## 2. Worksheet generation (real scenarios)
```
$ python3 build_worksheet.py
wrote .../relabel_worksheet.csv  (126 episodes across 42 scenarios)
wrote .../machine_baseline.json
{
  "n_episodes": 126,
  "judge1_vs_judge1": {"cohen_kappa": 1.0, "percent_agreement": 1.0, ...},
  "judge1_vs_judge2": {"cohen_kappa": 0.917, "percent_agreement": 0.9603, ...},
  "label_distribution_judge1": {"CORRECT": 47, "WRONG": 79},
  "label_distribution_judge2": {"CORRECT": 52, "WRONG": 74}
}
```
PASS — 126 real episodes labelled by the actual deterministic judge.

## 3. CSV parse + schema check
```
$ head -1 relabel_worksheet.csv
episode_id,scenario,provenance,gold_root,red_herrings,stated_cause,machine_label,human_label,notes
$ wc -l relabel_worksheet.csv  -> 127 (header + 126)
```
Blinded copy generated (machine_label removed): 126 rows, 8 columns. PASS.

## 4. machine_baseline.json parse
```
$ python3 -c "import json;print('ok',list(json.load(open('machine_baseline.json')).keys()))"
ok ['n_episodes', 'judge1_vs_judge1', 'judge1_vs_judge2', 'label_distribution_judge1', 'label_distribution_judge2']
```
PASS.

## Fixes applied during development
- None required after first green run. The degenerate-kappa branch (identified in 05)
  was written in before testing, so `test_degenerate_constant_raters` passed first time.

## BLOCKER (documented, expected)
**Human relabeling is not available this week** — no recruited SRE annotators / annotation
budget. Therefore the *human-vs-human* and *human-vs-machine* kappa numbers cannot be
produced. This is the core scientific result the protocol exists to deliver, and it is
BLOCKED on human input, not on code. Everything needed to compute it the moment labels
arrive is built, tested, and primed (the blinded worksheet + the library calls listed in
04 section C step 4). Machine-vs-machine agreement is delivered as the sanity baseline in
its place.
