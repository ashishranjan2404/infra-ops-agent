# B13 — 04 Technical Spec

## A. IAA library (`iaa.py`)

Label type: any hashable (here strings `"CORRECT"` / `"WRONG"`). All functions pure.

```python
percent_agreement(a: Sequence, b: Sequence) -> float
    # P_o = mean(a[i]==b[i]); ValueError on len mismatch or empty.

cohen_kappa(a: Sequence, b: Sequence) -> float
    # kappa = (P_o - P_e)/(1 - P_e); P_e from each rater's marginals.
    # Degenerate (both constant => P_e==1): return 1.0 if agree else 0.0.

fleiss_kappa(table: Sequence[Sequence[int]]) -> float
    # table[i][j] = #raters assigning category j to item i; equal row sums n>=2.

krippendorff_alpha(matrix: Sequence[Sequence]) -> float
    # matrix[r][i] = rater r's label for item i, or None. Nominal metric.
    # Items rated by <2 raters excluded. ValueError if no item has >=2 ratings.

mean_pairwise_cohen(labels_by_rater: dict[str, Sequence]) -> float
    # mean Cohen kappa over all rater pairs; needs >=2 raters.
```

Interpretation bands (Landis & Koch, documented for the report, not enforced in code):
< 0 poor, 0.0-0.20 slight, 0.21-0.40 fair, 0.41-0.60 moderate, 0.61-0.80 substantial,
0.81-1.00 almost perfect.

## B. Worksheet generator (`build_worksheet.py`)

Episode panel per scenario (deterministic, no LLM): index 0 = gold description
(expected CORRECT), 1 = "the incident is caused by {first red herring}" (expected WRONG),
2 = generic "just overloaded / needs more replicas" (expected WRONG).

`episode_id` format: `"{scenario}#{j}"` (stable, unique).

### CSV schema `relabel_worksheet.csv`
| column | meaning |
|---|---|
| episode_id | `{scenario}#{j}` |
| scenario | scenario name |
| provenance | gold / herring / generic |
| gold_root | scenario.gold_root_description |
| red_herrings | ` | `-joined red_herring_hints |
| stated_cause | the candidate diagnosis to judge |
| machine_label | CORRECT/WRONG from `deterministic_judge` |
| human_label | BLANK — human fills CORRECT or WRONG |
| notes | BLANK — optional rationale |

### `machine_baseline.json`
```json
{
  "n_episodes": int,
  "judge1_vs_judge1": {"description": str, "cohen_kappa": 1.0, "percent_agreement": 1.0},
  "judge1_vs_judge2": {"description": str, "cohen_kappa": float, "percent_agreement": float},
  "label_distribution_judge1": {"CORRECT": int, "WRONG": int},
  "label_distribution_judge2": {"CORRECT": int, "WRONG": int}
}
```
judge1 = `deterministic_judge`; judge2 = `mechanism_score >= 0.5`.

## C. Human IAA protocol (run when annotators available)
1. **Recruit** >=2 SRE-literate annotators (3 preferred for Fleiss/Krippendorff).
2. **Blind**: ship each annotator a copy of `relabel_worksheet.csv` with the
   `machine_label` column DELETED. They fill `human_label` independently, no discussion.
3. **Collect** into `human_labels_<rater>.csv` keyed by `episode_id`.
4. **Compute** (each is a library call):
   - human-vs-human: `mean_pairwise_cohen({r: labels...})` and
     `krippendorff_alpha([rater rows])`.
   - human-vs-machine: `cohen_kappa(consensus_human, machine_label)`.
5. **Adjudicate** disagreements; tag judge errors by `provenance`/`scenario` to find
   systematic bias in the 30% reward term.
6. **Report** h-vs-h FIRST (task quality), then h-vs-machine (judge validity).

## D. Test cases (`test_iaa.py`)
perfect agreement -> 1.0; chance -> ~0; hand-computed Cohen kappa value; worse-than-chance
-> negative; degenerate constant raters; length-mismatch / empty raise; Fleiss perfect +
uneven-rater error; Krippendorff perfect, missing-data, partial disagreement; mean
pairwise + <2-rater error.

## E. Contracts / invariants
- No edits to `rex/*`, `sim/*`, `agent/*`, shared experiments. Read-only imports only.
- Stdlib only. Deterministic outputs (no RNG, no network, no LLM).
- machine_baseline `judge1_vs_judge1.cohen_kappa` MUST equal 1.0 (idempotence assertion).
