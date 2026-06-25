# B13 — 06 Implementation

## Artifacts built (all under `experiments/ralph_outputs/B13/artifacts/`)

1. **`iaa.py`** (zero-dependency IAA library)
   - `percent_agreement`, `cohen_kappa` (with degenerate-constant handling),
     `fleiss_kappa`, `krippendorff_alpha` (nominal, missing-data tolerant),
     `mean_pairwise_cohen`. Stdlib only (`collections`, `itertools`).

2. **`build_worksheet.py`** (generator + machine baseline)
   - Loads all 42 real scenarios via `rex.harness.load_scenario`.
   - Synthesises a deterministic 3-candidate panel per scenario (gold / first
     red-herring / generic), labels each with `rex.scoring.deterministic_judge`.
   - Writes `relabel_worksheet.csv` (126 episodes).
   - Computes `machine_baseline.json`: idempotence kappa (judge vs judge) and a
     second-grader kappa (judge vs `mechanism_score>=0.5`).

3. **`test_iaa.py`** — 13 pytest cases over the library.

4. Generated data:
   - **`relabel_worksheet.csv`** — 126 rows, blank `human_label`/`notes`.
   - **`relabel_worksheet_blinded.csv`** — same rows, `machine_label` column removed
     (the copy that ships to human annotators, per the blinding protocol in 04).
   - **`machine_baseline.json`** — real computed agreement numbers.

## Key numbers (real, from `python3 build_worksheet.py`)
- 126 episodes across 42 scenarios.
- judge1-vs-judge1 Cohen kappa = **1.0** (idempotence / sanity baseline).
- judge1-vs-judge2 Cohen kappa = **0.917**, percent agreement = **0.9603** (two
  different deterministic graders — the honest non-trivial machine baseline).
- Label distribution judge1: 47 CORRECT / 79 WRONG; judge2: 52 / 74.

## Shared-core safety
No edits to `rex/*.py`, `sim/*.py`, `agent/*.py`, or shared experiments. The scripts
only IMPORT `rex.harness` and `rex.scoring` read-only. No proposed core change was
needed, so no `.patch` was produced.

## How to run
```bash
cd experiments/ralph_outputs/B13/artifacts
python3 -m pytest test_iaa.py -q     # 13 passed
python3 build_worksheet.py           # regenerates CSV + machine_baseline.json
```
