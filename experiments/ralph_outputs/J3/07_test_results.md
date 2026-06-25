# 07 — Test Results

## Environment
- Python 3.13 (`python3`), stdlib only. cwd: `experiments/ralph_outputs/J3/artifacts/`.

## T0 — syntax / parse
```
$ python3 -m py_compile score_human_eval.py    -> compile OK
$ json.load(diagnoses_to_rate.json / blinding_key.json / results_example.json)  -> json OK
```
PASS.

## T1 — synthetic 5-rater self-test
```
$ python3 score_human_eval.py --out results_selftest.json
[synthetic-selftest] 5 raters x 12 items -> results_selftest.json
  correctness  mean=2.85 alpha=0.6304 within1=0.8583 (moderate / weak)
  usefulness   mean=2.85 alpha=0.7361 within1=0.9417 (acceptable ...)
  safety       mean=2.73 alpha=0.6351 within1=0.8833 (moderate / weak)
  validity (human vs auto reward), Spearman: correctness 0.943 / usefulness 0.79 / safety 0.92
```
PASS. Alpha values land in a plausible band for noisy ordinal data (0.63–0.74). Validity is
high *by construction* (synthetic truth was derived from auto_reward), which confirms the
correlation code reacts correctly when humans and the judge agree.

## T2 — real-CSV ingestion path == in-memory path
```
$ python3 score_human_eval.py --ratings 'ratings_example/*.csv' --out results_example.json
[real] 5 raters x 12 items -> results_example.json   (identical numbers to T1)
```
PASS. Proves the CSV reader, blinding-key join, and stats are consistent; the pipeline is ready
for real rater files.

## T3 — item/key alignment
```
T3 ids align: True n= 12
```
PASS. `diagnoses_to_rate.json` and `blinding_key.json` have identical 12 item_ids in order.

## T4 — missing rating cell (blank Likert) tolerated
```
T4 per_item usefulness_n (expect 1): 1
```
PASS. Blank cells are treated as missing (not 0), excluded from means, and counted via `_n`.

## T5 — degenerate all-identical ratings
```
T5 all-identical alpha: 1.0
```
PASS. Krippendorff alpha returns 1.0 when all raters agree perfectly (sanity check on the
ordinal coincidence-matrix implementation).

## Result
All 6 tests (T0–T5) PASS. The scoring pipeline, blinded rating set, key, rubric, protocol, and
CSV template are real and validated. No code defects outstanding.

## Documented BLOCKER
**Human recruitment.** The study cannot produce *real* IAA or *real* validity numbers until 5
eligible SREs are recruited and submit `ratings/sre{1..5}.csv`. Everything required to run the
analysis the instant they do is built and tested. The numbers above are from a synthetic
self-test (clearly labeled `_mode: synthetic-selftest`) and are **not** human results.
